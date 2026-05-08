# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _name = "stock.move"
    _inherit = ["stock.move", "datamatrix.mh10.mixin"]

class StockMoveLine(models.Model):
    _name = "stock.move.line"
    _inherit = ["stock.move.line", "datamatrix.mh10.mixin"]
