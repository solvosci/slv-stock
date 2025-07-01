# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_by_company_ids = fields.Many2many(
        'stock.company',
        compute='_compute_stock_by_company_template',
    )

    @api.depends('product_variant_ids.stock_by_company_ids', 'product_variant_count')
    def _compute_stock_by_company_template(self):
        for template in self:
            if template.product_variant_count <= 1 and template.detailed_type == 'product':
                template.stock_by_company_ids = template.product_variant_ids.stock_by_company_ids
            else:
                template.stock_by_company_ids = False
