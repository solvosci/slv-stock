# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    scale = fields.Boolean(string="Scales")
    mandatory_towing = fields.Boolean()
