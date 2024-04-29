# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _get_prepared_ls_returns(self):
        ls_list, to_ready = super()._get_prepared_ls_returns()
        moves_returned_sale = self.move_ids_without_package.filtered(
            lambda x: (
                x.origin_returned_move_id
                and x.sale_line_id
                and x.sale_line_id.ls_schedule_allowed
            )
        )
        if moves_returned_sale:
            ls_sale_list = [
                move.sale_line_id._prepare_logistics_schedule()
                for move in moves_returned_sale
            ]
            update_vals = {
                "type": "input",
                "scheduled_load_date": self.scheduled_date,
            }
            for ls_sale in ls_sale_list:
                ls_sale.update(update_vals)
            ls_list += ls_sale_list
            to_ready = True

        return ls_list, to_ready
