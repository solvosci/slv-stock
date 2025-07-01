# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class StockCompany(models.Model):
    _name = 'stock.company'
    _description = 'stock.company'

    product_id = fields.Many2one('product.product')
    company_id = fields.Many2one('res.company')
    quantity_available = fields.Float(digits='Product Unit of Measure')
    uom_id = fields.Many2one(related='product_id.uom_id')
