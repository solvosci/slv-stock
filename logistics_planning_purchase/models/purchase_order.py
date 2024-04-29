# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    logistics_schedule_ids = fields.One2many(
        comodel_name="logistics.schedule",
        inverse_name="purchase_order_id",
        string="Logistics Schedules",
        copy=False,
    )
    logistics_schedule_skip = fields.Boolean(
        default=False,
        copy=False,
        help="""
        Technical field that enables skip logistics schedules
        creation during order approval
        """,
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
    ls_transport_type = fields.Selection(
        related="incoterm_id.ls_sale_transport_type",
    )

    def _compute_logistics_account_moves(self):
        for po in self:
            po.logistics_account_move_ids = (
                po.order_line.logistics_schedule_ids.mapped("account_move_id")
                or False
            )
            po.logistics_account_move_count = len(
                po.logistics_account_move_ids
            )

    def action_view_ls_account_move(self):
        # TODO move every method to logistics_base_invoicing
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

    def button_approve(self):
        bad_order_lines = self.order_line.filtered(
            lambda x: x.ls_schedule_allowed and x.logistics_schedule_init <= 0
        )
        if bad_order_lines:
            bad_orders = bad_order_lines.order_id.mapped("name")
            raise ValidationError(
                _(
                    "Please fill a valid Initial required schedules (>=0)"
                    " for every order line for the following orders: %s"
                ) % ", ".join(bad_orders)
            )
        res = super().button_approve()
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
