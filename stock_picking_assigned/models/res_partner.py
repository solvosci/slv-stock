# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, _


class ResPartner(models.Model):
    _inherit = "res.partner"

    wms_code = fields.Integer()
