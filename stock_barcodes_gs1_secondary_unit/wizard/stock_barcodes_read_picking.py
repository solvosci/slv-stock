# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api, _


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    secondary_unit_qty = fields.Integer(default=1)

    @api.onchange('secondary_unit_qty')
    def _onchange_secondary_unit_qty(self):
        if self.barcode:
            product_qty = self.env["gs1_barcode"].decode(self.barcode).get("37", 0.0)
            self.product_qty = product_qty * self.secondary_unit_qty

    def update_fields_after_process_stock(self, moves):
        move_line_id = moves.move_line_ids.filtered(lambda x: x.lot_id == self.lot_id)[0]
        if self.product_qty == move_line_id.qty_done:
            move_line_id.secondary_uom_qty = self.secondary_unit_qty
        else:
            move_line_id.secondary_uom_qty += self.secondary_unit_qty
        if not move_line_id.secondary_uom_id and move_line_id.product_id.stock_secondary_uom_id:
            move_line_id.secondary_uom_id = move_line_id.product_id.stock_secondary_uom_id

        self.secondary_unit_qty = 1
        super(WizStockBarcodesReadPicking, self).update_fields_after_process_stock(moves)
