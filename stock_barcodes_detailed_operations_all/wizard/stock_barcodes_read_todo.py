# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class WizStockBarcodesReadTodo(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.todo"

    def operation_quantities(self):
        self.wiz_barcode_id.location_dest_id = self.location_dest_id
        return super().operation_quantities()
