# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def lines_summary_by_product(self):
        self.ensure_one()
        summary_dict = {}

        for product in self.move_line_ids.mapped("product_id"):
            lines = self.move_line_ids.filtered(
                lambda x: x.product_id.id == product.id
            )
            summary_dict[product.id] = {
                "count": len(lines),
                "sum": sum(lines.mapped("qty_done")),
            }
        
        return summary_dict
