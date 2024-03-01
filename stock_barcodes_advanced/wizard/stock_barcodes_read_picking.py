# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def update_fields_after_process_stock(self, moves):
        self.product_id = False
        self.product_qty = 0
        self.lot_id = False
        self.pending_move_ids._compute_qty_done()
        super(WizStockBarcodesReadPicking, self).update_fields_after_process_stock(moves)

    def _process_stock_move_line(self):
        res = super(WizStockBarcodesReadPicking, self)._process_stock_move_line()
        if res:
            for move_line_id, qty in res.items():
                ml_id = self.env['stock.move.line'].browse(move_line_id)
                ml_id.picking_id.do_unreserve()
                ml_id.product_uom_qty = ml_id.qty_done
                self.env['stock.quant']._update_reserved_quantity(ml_id.product_id, ml_id.location_id, qty, ml_id.lot_id)
        return res


class WizCandidatePicking(models.TransientModel):
    _inherit = "wiz.candidate.picking"

    qty_demand_product = fields.Float(compute='compute_qty_product', store=True)
    qty_done_product = fields.Float(compute='compute_qty_product', store=True)

    @api.depends('wiz_barcode_id.product_id')
    def compute_qty_product(self):
        for record in self:
            product_id = record.wiz_barcode_id.product_id
            move_ids = record.picking_id.move_ids_without_package.filtered(lambda x: x.product_id == product_id)
            record.qty_demand_product = sum(move_ids.mapped('product_uom_qty'))
            record.qty_done_product = sum(move_ids.mapped('quantity_done'))
