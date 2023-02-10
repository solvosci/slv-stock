# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    standard_price_warehouse_ids = fields.Many2many(
        comodel_name="product.average.price",
        compute="_compute_standard_price_warehouse_ids",
    )
    standard_price_warehouse_count = fields.Integer(
        compute="_compute_standard_price_warehouse_ids",
    )
    warehouse_valuation = fields.Boolean(
        related="categ_id.warehouse_valuation",
    )

    def _compute_standard_price_warehouse_ids(self):
        for product_tmpl in self:
            product_tmpl.standard_price_warehouse_ids = (
                product_tmpl.product_variant_count == 1
                and product_tmpl.product_variant_ids.standard_price_warehouse_ids
                or False
            )
            product_tmpl.standard_price_warehouse_count = len(
                product_tmpl.standard_price_warehouse_ids
            )
