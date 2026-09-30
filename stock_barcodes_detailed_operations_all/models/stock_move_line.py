# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def action_barcode_detailed_operation_unlink(self):
        wiz_barcode = self.env["wiz.stock.barcodes.read.picking"].browse(
            self.env.context.get("wiz_barcode_id", False)
        )
        self.move_id.barcode_backorder_action = "pending"
        self.unlink()
        if wiz_barcode:
            wiz_barcode.fill_todo_records()
            wiz_barcode.determine_todo_action()
