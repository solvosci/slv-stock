# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

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

    def review_relative_line_purchase(self, so_order_name, so_order_id):
        """ If some SO are cancelled or line deleted
            if purchase line state is draft, we can delete it
            else we need to put an activity in PO
        """
        po_to_notify_map = {}  # map PO -> recordset of SOL
        po_to_review_origin = []

        for po_line in self:
            if po_line.state not in ('purchase', 'done'):
                if po_line.order_id.origin \
                        and po_line.order_id not in po_to_review_origin:
                    po_to_review_origin += [po_line.order_id]
                po_line.unlink()
            else:
                if po_line.state != 'cancel':
                    po_to_notify_map.setdefault(
                        po_line.order_id,
                        self.env['sale.order.line']
                    )
                    po_to_notify_map[po_line.order_id] |= po_line.sale_line_id
        # remove this SO in origin of PO
        for po in po_to_review_origin:
            origins = po.origin.split(', ')
            if so_order_name in origins:
                po_lines = po.order_line.filtered(
                    lambda x: x.sale_line_id.order_id.id == so_order_id
                )
                if not po_lines:
                    origins.remove(so_order_name)
                    po.write({
                        'origin': ', '.join(origins)
                    })
        return po_to_notify_map
