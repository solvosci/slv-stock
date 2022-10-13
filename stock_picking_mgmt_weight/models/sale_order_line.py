# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models, api
from odoo.tools.float_utils import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    qty_cancelled = fields.Float(
        digits="Product Unit of Measure",
        string="Cancelled Quantity",
        readonly=True,
        help="Quantities affected by 'Cancel Pending' process",
    )
    is_cancellable = fields.Boolean(compute="_compute_is_cancellable")
    pending_qty = fields.Float(
        compute="_compute_pending_qty",
        string="Pending Quantity",
        digits="Product Unit of Measure",
        store=True,
    )
    has_pending_qty = fields.Boolean(
        compute="_compute_pending_qty",
        store=True,
        readonly=True,
        help="Technical field for sale order has pending quantity computation",
    )

    supply_condition_id = fields.Many2one(comodel_name="supply.condition")
    vehicle_type_id = fields.Many2one(comodel_name="vehicle.type")

    @api.depends("product_uom_qty", "qty_delivered", "qty_cancelled")
    def _compute_pending_qty(self):
        for line in self:
            line.pending_qty = max(
                line.product_uom_qty - line.qty_delivered - line.qty_cancelled,
                0.0
            )
            # We only take in account positive pending quantities
            #  (legacy code, it used to be negative, so we don't use
            #   float_is_zero)
            line.has_pending_qty = (
                float_compare(
                    line.pending_qty,
                    0,
                    precision_rounding=line.product_uom.rounding or 0.001
                ) == 1
            )

    def _compute_is_cancellable(self):
        for line in self:
            # TODO float_compare
            line.is_cancellable = (
                line.order_id.state in ["sale", "done"]
                and line.pending_qty > 0.0
            )

    def action_cancel_pending_line(self):
        self.ensure_one()
        self.order_id.action_cancel_pending(custom_line=self)
