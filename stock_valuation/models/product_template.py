# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price_warehouse_ids = fields.One2many('product.average.price', 'product_id')
    warehouse_valuation = fields.Boolean(
        related="categ_id.warehouse_valuation",
    )
