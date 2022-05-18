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
            line.pending_qty = (
                line.product_uom_qty - line.qty_delivered - line.qty_cancelled
            )
            # We only take in account positive pending quantities
            #  (it's possible to be negative)
            line.has_pending_qty = (
                float_compare(
                    line.pending_qty,
                    0,
                    precision_rounding=line.product_uom.rounding or 0.001
                ) == 1
            )
