# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields


class StockQuant(models.Model):
    _inherit = "stock.quant"

    inventory_quantity_secondary_uom = fields.Float(
        compute="_compute_inventory_quantity_secondary_uom",
        string="Quant in 2nd unit",
        compute_sudo=True,
    )
    product_stock_secondary_uom_id = fields.Many2one(
        related="product_id.stock_secondary_uom_id",
        string="2nd unit",
    )

    def _compute_inventory_quantity_secondary_uom(self):
        """
        For those products that have a valid secondary unit, available quantity
        for this 2nd unit is displayed, based on unit factor
        """
        quants = self.filtered(
            lambda x: (
                x.product_id.stock_secondary_uom_id
                and x.product_id.stock_secondary_uom_id.factor > 0.0
            )
        )
        for quant in quants:
            quant.inventory_quantity_secondary_uom = (
                quant.quantity
                /
                quant.product_id.stock_secondary_uom_id.factor
            )
        (self - quants).write({
            "inventory_quantity_secondary_uom": 0.0,
        })
