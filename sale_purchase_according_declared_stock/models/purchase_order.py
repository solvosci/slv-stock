# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # TODO: Do we also want to add the picking status to the purchase order tree view?
    # TODO check if you have to do something different than what is done in sale_purchase when the purchase is canceled
    def button_confirm(self):
        result = super().button_confirm()
        self._create_detailed_operations()
        return result

    def _create_detailed_operations(self):
        pick_ids = self.picking_ids.filtered(
            lambda l: l.state == 'assigned')
        for p in pick_ids:
            move_lines = []
            for move_line in p.move_line_ids:
                move_lines.append([0, 0, {
                    'picking_id': move_line.picking_id.id,
                    'move_id': move_line.move_id.id,
                    'product_id': move_line.product_id.id,
                    'product_uom_id': move_line.product_uom_id.id,
                    'qty_done': move_line.product_uom_qty,
                    'location_id': move_line.location_id.id,
                    'location_dest_id': move_line.location_dest_id.id,
                    'company_id': move_line.company_id.id,
                }])
            p.write({'move_line_nosuggest_ids': move_lines})


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    move_dest_ids = fields.Many2many('stock.move',
                                     String='Downstream  Moves',
                                     copy=False)
