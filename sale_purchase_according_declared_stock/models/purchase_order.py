# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

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
        num_pickings = 0
        pick_ids = self.picking_ids.filtered(
            lambda l: l.state != 'cancel')
        for p in pick_ids:
            if p.state == 'assigned':
                num_pickings += 1
        if num_pickings > 0:
            for p in pick_ids:
                for move_line in p.move_line_ids:
                    vals = {
                        'picking_id': move_line.picking_id.id,
                        'product_id': move_line.product_id.id,
                        'product_uom_id': move_line.product_uom_id.id,
                        'qty_done': move_line.product_uom_qty,
                        'location_id': move_line.location_id.id,
                        'location_dest_id': move_line.location_dest_id.id,
                    }
                    self.env['stock.move.line'].create(vals)