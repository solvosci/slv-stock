# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    partner_vat = fields.Char(related="partner_id.vat")
