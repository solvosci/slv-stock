# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    warehouse_valuation_close_date = fields.Date()
