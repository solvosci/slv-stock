# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_done(self):
        ret = True
        for pick in self:
            pick = pick.with_context(stock_move_custom_date=pick.scheduled_date)
            ret |= super(StockPicking, pick)._action_done()
            pick.date_done = pick.scheduled_date
        return ret
