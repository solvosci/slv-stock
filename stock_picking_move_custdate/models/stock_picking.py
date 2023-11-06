# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    effective_planned_date = fields.Datetime(
        string="Effective planned date",
        copy=False,
        tracking=True,
        states={"done": [("readonly", True), ("invisible", True)], "cancel": [("readonly", True), ("invisible", True)]},
        help=
        """
        When filled, moves for this picking will be saved
        with this date.
        Leave blank if default behavior is required.
        """,
    )

    def _action_done(self):
        ret = False
        cust_date_pick = self.filtered(lambda x: x.effective_planned_date)
        for pick in cust_date_pick:
            pick = pick.with_context(stock_move_custom_date=pick.effective_planned_date)
            ret |= super(StockPicking, pick)._action_done()
            pick.date_done = pick.effective_planned_date
        ret |= super(StockPicking, self - cust_date_pick)._action_done()
        return ret
