# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    require_same_carrier_in_batch = fields.Boolean()
