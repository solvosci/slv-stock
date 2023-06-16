# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    official_commercial_name = fields.Char()
    fao = fields.Char()
    fcd_expiration_days = fields.Integer('Expiration Days')
    caliber = fields.Char()
    presentation_id = fields.Many2one('fcd.presentation')
