# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        custom_date = self.env.context.get("stock_move_custom_date", False)
        moves = super()._action_done(cancel_backorder=cancel_backorder)
        if moves and custom_date:
            moves.move_line_ids.write({"date": custom_date})
            moves.write({"date": custom_date})
