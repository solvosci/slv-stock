# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def update_fields_after_process_stock(self, moves):
        self.product_id = False
        self.product_qty = 0
        self.lot_id = False
        self.pending_move_ids._compute_qty_done()
        super(WizStockBarcodesReadPicking, self).update_fields_after_process_stock(moves)
