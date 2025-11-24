# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = ['product.template']

    tracking = fields.Selection(
        [
            ('serial', 'By Unique Serial Number'),
            ('lot', 'By Lots'),
            ('none', 'No Tracking'),
        ],
        tracking=True,
    )
