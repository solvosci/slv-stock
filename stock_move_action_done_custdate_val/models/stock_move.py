# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        custom_date = self.env.context.get("stock_move_custom_date", False)
        moves = super()._action_done(cancel_backorder=cancel_backorder)
        if moves and custom_date:
            # datetime to date timezone workaround
            moves.sudo().account_move_ids.date_update_from_datetime(
                custom_date
            )
            # create_date must be updated with a cr.execute statement
            moves.sudo().stock_valuation_layer_ids.create_date_update(
                custom_date
            )
        return moves
