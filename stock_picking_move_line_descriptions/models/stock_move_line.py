# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    description = fields.Char(related='move_id.name')
