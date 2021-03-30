# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def lines_category_product(self):
        self.ensure_one()
        categories = {}
        
        category_attribute = self.env.ref("stock_picking_eco_tag.product_attribute_category").id
        for product in self.move_line_ids.mapped("product_id"):
            categories[product.id] = ""
            for attribute in product.attribute_line_ids.filtered(
                lambda x: x.attribute_id.id == category_attribute
            ):
                categories[product.id] = attribute.value_ids and attribute.value_ids[0].name or ""
                
        return categories
