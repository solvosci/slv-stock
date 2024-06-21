# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields

class StockPickingBatchSplit(models.TransientModel):
    _name="stock.picking.batch.split.wizard"
    _description="Split picking"

    product_ids = fields.Many2many("product.product")
    batch_id = fields.Many2one("stock.picking.batch")
    batch_product_ids = fields.Many2many("product.product", compute="_compute_batch_product_ids")

    def split(self):
        move_ids = self.batch_id.move_lines.filtered(lambda x: x.product_id in self.product_ids)
        picking_ids = move_ids.mapped('picking_id')
        for picking in picking_ids:
            wizard_id = self.env['stock.split.picking'].create({
                'mode': 'selection',
                'picking_ids': [(4, picking.id)],
                'move_ids': [(4, move.id) for move in move_ids.filtered(lambda x: x.picking_id == picking)]
            })
            wizard_id.action_apply()

    def _compute_batch_product_ids(self):
        for record in self:
            record.batch_product_ids = record.batch_id.move_lines.mapped('product_id')
