# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductCategory(models.Model):
    _inherit = "product.category"

    product_label_template_id = fields.Many2one("product.label.template")
