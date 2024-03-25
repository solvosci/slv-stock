# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MoveWeight(models.TransientModel):
    _inherit = "stock.move.weight.wizard"

    def purchase_order_new(self):
        order_new = super().purchase_order_new()
        # We want to prevent logistics schedules creation from
        #  classification orders
        order_new.logistics_schedule_skip = True
        return order_new
