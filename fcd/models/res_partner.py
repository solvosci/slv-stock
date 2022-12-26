# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    second_name_fcd = fields.Char("Second Name")
