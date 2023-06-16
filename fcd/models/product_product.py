# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    fcd_document_ids = fields.One2many('fcd.document','product_id')
    fcd_document_count = fields.Integer('fcd.document', compute='_compute_fcd_document_count')

    def _compute_fcd_document_count(self):
        for product in self:
            product.fcd_document_count = len(product.fcd_document_ids)
