# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    block_direct_edit_qty_done = fields.Boolean(related="picking_id.picking_type_id.block_direct_edit_qty_done")
