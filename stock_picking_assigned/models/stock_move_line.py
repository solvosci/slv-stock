# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    recounted = fields.Boolean(default=False, copy=False)
