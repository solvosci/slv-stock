# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    standard_price_warehouse_ids = fields.One2many('product.average.price', 'product_id')
    standard_price_warehouse_count = fields.Integer(
        compute="_compute_standard_price_warehouse_ids",
    )

    def _compute_standard_price_warehouse_ids(self):
        for product in self:
            product.standard_price_warehouse_count = len(
                product.standard_price_warehouse_ids
            )

