# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _get_state_among_origin_moves(self):
        moves_todo = self.filtered(lambda m: m.state not in ['cancel', 'done'])
        for move in moves_todo:
            if any(origin_move.state in
                   ['draft', 'waiting', 'assigned', 'partially_available']
                   for origin_move in move.move_orig_ids):
                return 'waiting'
        return 'assigned'
