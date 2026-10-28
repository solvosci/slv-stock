# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = "stock.move"

    block_direct_edit_qty_done = fields.Boolean(related="picking_id.picking_type_id.block_direct_edit_qty_done")
    has_move_lines = fields.Boolean(
        compute='_compute_has_move_lines',
    )

    @api.depends('move_line_ids')
    def _compute_has_move_lines(self):
        for move in self:
            move.has_move_lines = bool(move.move_line_ids)
