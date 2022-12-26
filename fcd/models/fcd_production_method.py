# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class FcdProductionMethod(models.Model):
    _name = 'fcd.production.method'
    _description = 'fcd.production.method'

    name = fields.Char()
