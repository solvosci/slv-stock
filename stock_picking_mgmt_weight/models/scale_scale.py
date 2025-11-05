# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields

class Scale(models.Model):
    _inherit = 'scale.scale'

    valid_weight_max_age_secs = fields.Integer(default=10)

