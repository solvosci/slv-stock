# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        return super(
            StockBackorderConfirmation,
            self.with_context(skip_partner=True)
        ).process()


    def process_cancel_backorder(self):
        return super(
            StockBackorderConfirmation,
            self.with_context(skip_partner=True)
        ).process_cancel_backorder()
