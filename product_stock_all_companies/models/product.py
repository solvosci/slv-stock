# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_by_company_ids = fields.Many2many(
        'stock.company',
        compute_sudo=True,
        compute='_compute_stock_by_company_ids',
    )

    @api.depends('qty_available')
    def _compute_stock_by_company_ids(self):
        companies = self.env['res.company'].search([])

        for product in self:
            result = []
            for company in companies:

                product_in_ctx = product.with_context(
                    allowed_company_ids=[company.id]
                )
                qty = product_in_ctx.qty_available

                result.append((0, 0, {
                    'product_id': product.id,
                    'company_id': company.id,
                    'quantity_available': qty,
                }))
            product.stock_by_company_ids = result
