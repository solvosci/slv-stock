# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_prepared_ls_returns(self):
        ls_list, to_ready = super()._get_prepared_ls_returns()
        moves_returned_purchase = self.move_ids_without_package.filtered(
            lambda x: (
                x.origin_returned_move_id
                and x.purchase_line_id
                and x.purchase_line_id.ls_schedule_allowed
            )
        )
        if moves_returned_purchase:
            ls_purchase_list = [
                move.purchase_line_id._prepare_logistics_schedule()
                for move in moves_returned_purchase
            ]
            update_vals = {
                "type": "output",
                "scheduled_load_date": self.scheduled_date,
            }
            for ls_purchase in ls_purchase_list:
                ls_purchase.update(update_vals)
            ls_list += ls_purchase_list
            to_ready = True

        return ls_list, to_ready
