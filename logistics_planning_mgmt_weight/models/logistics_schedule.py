# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models

import ast


class LogisticsSchedule(models.Model):
    _inherit = "logistics.schedule"

    supply_condition_id = fields.Many2one(
        comodel_name="supply.condition",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )

    @api.depends("stock_move_id.net_weight")
    def _compute_product_uom_qty(self):
        super()._compute_product_uom_qty()
        for record in self.filtered(lambda x: x.stock_move_id.net_weight > 0.0):
            record.product_uom_qty = record.stock_move_id.net_weight

    @api.onchange("stock_move_id")
    def _onchange_stock_move_id(self):
        super()._onchange_stock_move_id()
        upd_values = {}
        sm_sudo = self.sudo().stock_move_id
        if not sm_sudo:
            # TODO clean some values?
            pass
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
            self.write(upd_values)

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
