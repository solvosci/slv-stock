# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models

class StockPicking(models.Model):
    _inherit = "stock.picking"

    deliver_to = fields.Char()
