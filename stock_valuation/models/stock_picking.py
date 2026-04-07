# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    has_val_cust_ret_date = fields.Boolean(
        string="Valuation - Has Customer Return Date",
        default=False,
    )
    val_cust_ret_date = fields.Datetime(
        string="Valuation - Customer Return Date",
        compute="_compute_val_cust_ret_date",
        store=True,
        readonly=False,
    )
    has_val_cust_ret_date_enabled = fields.Boolean(
        string="Valuation - Customer Return Date Enabled",
        compute="_compute_has_val_cust_ret_date_attrs",
    )
    has_val_cust_ret_date_visible = fields.Boolean(
        string="Valuation - Customer Return Date Visible",
        compute="_compute_has_val_cust_ret_date_attrs",
    )

    @api.depends("has_val_cust_ret_date")
    def _compute_val_cust_ret_date(self):
        # When has_val_cust_ret_date is set, if there's no value yet, current date is set
        # When has_val_cust_ret_date is unset, the value is cleared
        pick_cust_date = self.filtered(lambda x: x.has_val_cust_ret_date)
        pick_cust_date_empty = self.filtered(
            lambda x: not x.val_cust_ret_date
        )
        pick_cust_date_empty.update({"val_cust_ret_date": fields.Datetime.now()})
        (self - pick_cust_date).update({"val_cust_ret_date": False})

    @api.depends("picking_type_code", "move_lines.purchase_line_id", "state")
    def _compute_has_val_cust_ret_date_attrs(self):
        for picking in self:
            # We'll only enable fill a custom return date for in-process incoming returns
            picking.has_val_cust_ret_date_visible = (
                picking.picking_type_code == "outgoing"
                and picking.move_lines.purchase_line_id   # and picking.move_lines.origin_returned_move_id
            )
            picking.has_val_cust_ret_date_enabled = (
                picking.has_val_cust_ret_date_visible
                and not picking.state in ["done", "cancel"]
            )

    @api.constrains("val_cust_ret_date")
    def _check_val_cust_ret_date(self):
        for picking in self.filtered(lambda x: x.has_val_cust_ret_date):
            purchase_order_id = picking.move_lines.purchase_line_id.order_id
            if purchase_order_id and purchase_order_id.date_order > picking.val_cust_ret_date:
                raise ValidationError(
                    _(
                        "Customer return date for %s cannot be prior than"
                        " original returned %s date"
                    ) % (
                        picking.name,
                        purchase_order_id.name,
                    )
                )            