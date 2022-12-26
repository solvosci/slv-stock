# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    product_qty_secondary_uom = fields.Float(
        compute="_compute_product_qty_secondary_uom",
        string="Quantity in 2nd unit",
        compute_sudo=True,
    )
    product_secondary_uom_id = fields.Many2one(
        related="product_id.stock_secondary_uom_id",
        string="2nd unit",
    )

    def _compute_product_qty_secondary_uom(self):
        """
        read_group() is used because we want to show product_qty_secondary_uom
        in tree views
        """
        fetch_data = self.env["stock.quant"].read_group(
            [
                ("lot_id", "in", self.ids),
                ("location_id.usage", "=", "internal"),
            ],
            ["lot_id", "quantity:sum"],
            ["lot_id"],
            lazy=False,
        )
        result = {
            data["lot_id"][0]: data["quantity"]
            for data in fetch_data
        }
        for lot in self:
            secondary_uom_factor = (
                lot.product_id.stock_secondary_uom_id
                and lot.product_id.stock_secondary_uom_id.factor
            )
            lot.product_qty_secondary_uom = (
                result.get(lot.id, 0.0) / secondary_uom_factor if secondary_uom_factor
                else 0.0
            )
