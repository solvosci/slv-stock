# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero


class SaleOrder(models.Model):
    _inherit = "sale.order"

    logistics_schedule_ids = fields.One2many(
        comodel_name="logistics.schedule",
        inverse_name="sale_order_id",
        string="Logistics Schedules",
        copy=False,
    )
    logistics_schedule_disabled = fields.Boolean(
        string="Disable logistics schedules creation",
        default=False,
        copy=False,
        readonly=False,        
        states={
            "cancel": [("readonly", True)],
            "done": [("readonly", True)],
        },
        tracking=True,
    )
    logistics_account_move_ids = fields.Many2many(
        comodel_name="account.move",
        compute="_compute_logistics_account_moves",
        string="Logistics Bills",
    )
    logistics_account_move_count = fields.Integer(
        compute="_compute_logistics_account_moves",
        string="Logistics Bill Count",
    )

    @api.onchange("warehouse_id")
    def _ls_onchange_warehouse_id(self):
        if self.warehouse_id:
            self.logistics_schedule_disabled = (
                self.warehouse_id.ls_so_create_disable_default
            )

    def _compute_logistics_account_moves(self):
        for so in self:
            so.logistics_account_move_ids = (
                so.order_line.logistics_schedule_ids.mapped("account_move_id")
                or False
            )
            so.logistics_account_move_count = len(
                so.logistics_account_move_ids
            )

    def action_view_ls_account_move(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_in_invoice_type")
        result = action.read()[0]
        result["context"] = {
            "default_type": "in_invoice",
            "default_company_id": self.company_id.id,
        }
        # Invoice_ids may be filtered depending on the user. To ensure we get all
        # bills, we read them in sudo to fill the cache.
        # self.sudo()._read(['invoice_ids'])
        # choose the view_mode accordingly
        if self.logistics_account_move_count > 1:
            result["domain"] = "[('id', 'in', " + str(self.logistics_account_move_ids.ids) + ")]"
            # result["domain"] = [("id", "in", self.logistics_account_move_ids.ids)]
        else:
            res = self.env.ref("account.view_move_form", False)
            form_view = [(res and res.id or False, "form")]
            if "views" in result:
                result["views"] = form_view + [(state,view) for state,view in action["views"] if view != "form"]
            else:
                result["views"] = form_view
            result["res_id"] = self.logistics_account_move_ids.id or False
        return result        

    def action_confirm(self):
        # If there are already logistics schedules linked to this SO we won't
        #  re-create them. Such situation occurs e.g. when SO was previously
        #  cancelled and set back to quotation
        skip_ls_process = bool(self.logistics_schedule_ids)
        if not skip_ls_process:
            bad_order_lines = self.order_line.filtered(
                lambda x: x.ls_schedule_allowed and x.logistics_schedule_init <= 0
            )
            pd = self.env["decimal.precision"].precision_get("Product Price")
            zero_price_order_lines = self.order_line.filtered(
                lambda x: x.ls_schedule_allowed and float_is_zero(x.logistics_price_unit, precision_rounding=pd)
            )
            error_msgs = []
            if bad_order_lines:
                bad_orders = bad_order_lines.order_id.mapped("name")
                error_msgs.append(
                    _(
                        "Please fill a valid Initial required schedules (>=0)"
                        " for every order line for the following orders: %s"
                    ) % ", ".join(bad_orders)
                )
            if zero_price_order_lines:
                zero_price_orders = zero_price_order_lines.order_id.mapped("name")
                error_msgs.append(
                    _(
                        "Please fill a valid Logistics Price Unit (>0)"
                        " for every order line for the following orders: %s"
                    ) % ", ".join(zero_price_orders)
                )
            if error_msgs:
                raise ValidationError("\n\n".join(error_msgs))

        res = super().action_confirm()
        if not skip_ls_process:
            ls_values = []
            for line in self.order_line.filtered(lambda x: x.ls_schedule_allowed):
                ls_values += [
                    line._prepare_logistics_schedule()
                    for i in range(0, line.logistics_schedule_init)
                ]
            if ls_values:
                ls_ids = self.env["logistics.schedule"].sudo().create(ls_values)
                ls_ids._action_ready()
        return res

    def write(self, values):
        ret = super().write(values)
        self._update_logistics_schedules(values)
        return ret

    def _update_logistics_schedules(self, values):
        """
        We add here those sale order values that should be hardlinked
        to logistics schedules
        """
        ls_ids = self.sudo().logistics_schedule_ids.filtered(
            lambda x: x.state not in ["done", "cancel"]
        )
        if ls_ids:
            upd_values = {}
            if "warehouse_id" in values:
                upd_values[
                    "destination_partner_id"
                ] = self.warehouse_id.partner_id.id
            if "partner_shipping_id" in values:
                upd_values["partner_id"] = self.partner_shipping_id.id
            if "incoterm" in values:
                upd_values["incoterm_id"] = self.incoterm.id
            if upd_values:
                ls_ids.write(upd_values)
