# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    signature = fields.Image(
        'Signature',
        help='Signature',
        copy=False,
        attachment=True,
    )
