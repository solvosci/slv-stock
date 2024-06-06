# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

import ast


class LogisticsSchedule(models.Model):
    _inherit = "logistics.schedule"

    supply_condition_id = fields.Many2one(
        comodel_name="supply.condition",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    extra_stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        states={
            "draft": [("readonly", True)],
            "cancel": [("readonly", True)],
            "done": [("readonly", True)],
        },
        string="Other tickets",
    )

    @api.depends("stock_move_id.net_weight", "extra_stock_move_ids.net_weight")
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for record in self.filtered(lambda x: x.stock_move_id.net_weight > 0.0):
            record.product_uom_qty = sum(
                (record.stock_move_id | record.extra_stock_move_ids).mapped("net_weight")
            )

    @api.onchange("stock_move_id")
    def _onchange_stock_move_id(self):
        self_ctx = self.with_context(sched_finish_input_auto=False)
        super(LogisticsSchedule, self_ctx)._onchange_stock_move_id()
        upd_values = {}
        sm_sudo = self.sudo().stock_move_id
        if not sm_sudo:
            # TODO clean some values?
            if self.extra_stock_move_ids:
                raise UserError(_(
                    "Cannot remove ticket from schedule, because it has extra"
                    " tickets already linked. Please remove them first"
                )
            )
        elif self.sale_order_line_id or sm_sudo.picking_code == "internal":
            # Output from a sales order or internal transfer (for manual outputs)
            upd_values.update({
                "license_plate_1": sm_sudo.picking_id.vehicle_id.name,
                "license_plate_2": (
                    self.picking_id.towing_license_plate
                    if self.transport_type == "ground"
                    else self.picking_id.container_number
                ),
            })
        elif sm_sudo.net_weight > 0:
            # Input from a ticket
            upd_values.update({
                "license_plate_1": sm_sudo.picking_vehicle_id.name,
                "license_plate_2": sm_sudo.picking_towing_license_plate,
            })

        if upd_values:
            self.update(upd_values)

    def _action_ready_fields_check_req_fields(self):
        fields = super()._action_ready_fields_check_req_fields()
        fields.update({
            "supply_condition_id": _("Supply Condition"),
        })
        return fields

    def action_logistics_schedule_create_input_ticket(self):
        action = self.env.ref(
            "stock_picking_mgmt_weight.stock_move_weights_in_progress"
        )
        result = action.read()[0]
        ctx = ast.literal_eval(result.get("context"))
        # TODO picking_partner_id and picking_vehicle_id propagation don't work (as related stored?)
        # TODO incomplete ticket problem
        ctx.update({
            "default_logistics_schedule_id": self.id,
            "default_product_id": self.product_id.id,
            "default_aux_picking_partner_id": self.partner_id.id,
            "default_aux_picking_vehicle_id": (
                self.env["vehicle.vehicle"].search(
                    [("name", "=", self.license_plate_1)], limit=1
                ).id or False
            ),
        })
        result["context"] = ctx
        res = self.env.ref(
            "stock_picking_mgmt_weight.stock_move_mgmt_weight_frontend_weight_form_view",
            False
        )
        form_view = [(res and res.id or False, "form")]
        result["views"] = form_view

        return result
    
    def action_logistics_schedule_finish(self):
        # TODO confirm wizard?
        self._action_sched_finished()

    def _check_safe_finished(self):
        super()._check_safe_finished()
        wrong_finished = self.filtered(
            lambda x: (
                x.type == "input" and (
                    len((x.stock_move_id | x.extra_stock_move_ids).filtered(lambda x: x.net_weight <= 0.0)) > 0
                )
            )
        )
        if wrong_finished:
            raise UserError(
                _(
                    "One or more of the selected schedules cannot be marked as"
                    " finished because one of their tickets are still"
                    " uncomplete (without net weight). Please check them"
                )
            )

    def write(self, values):
        check_extra_moves = ("extra_stock_move_ids" in values)
        if check_extra_moves:
            # We assume that only a record is selected, no "expected singleton" should be fired
            old_extra_stock_move_ids = self.extra_stock_move_ids
        ret = super().write(values)
        if check_extra_moves:
            (self.extra_stock_move_ids - old_extra_stock_move_ids).write({
                "logistics_schedule_id": self.id,
            })
            (old_extra_stock_move_ids - self.extra_stock_move_ids).write({
                "logistics_schedule_id": False,
            })
        return ret
