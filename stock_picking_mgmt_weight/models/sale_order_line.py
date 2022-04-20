# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models, api


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pending_qty = fields.Float(
        compute="_compute_pending_qty",
        digits="Product Unit of Measure",
        store=True
    )

    supply_condition_id = fields.Many2one(comodel_name="supply.condition")
    vehicle_type_id = fields.Many2one(comodel_name="vehicle.type")

    @api.depends('product_uom_qty', 'qty_delivered')
    def _compute_pending_qty(self):
        for line in self:
            line.pending_qty = line.product_uom_qty - line.qty_delivered
