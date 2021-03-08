# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero, float_round


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _review_intermediate_transfers(self):
        pd = 1
        # how many is reserved and done by product and lot in this picking
        picking_moves = self.move_line_ids.filtered(
            lambda x: x.product_id.tracking != "none"
            and x.product_id.auto_create_lot
            and x.state not in ('done', 'cancel')).sorted(
            key='product_id')
        grouped_by_lot = []
        picking_product_ids = []
        for move in picking_moves:
            if move.product_id.id not in picking_product_ids:
                picking_product_ids += [move.product_id.id]
            reg_found = False
            for reg in grouped_by_lot:
                if reg['product_id'] == move.product_id.id \
                        and reg['lot_id'] == move.lot_id.id:
                    reg['product_qty'] += move.product_qty
                    reg['qty_done'] += move.qty_done
                    reg_found = True
            if not reg_found:
                grouped_by_lot.append({
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom_id.id,
                    'lot_id': move.lot_id.id,
                    'product_qty': move.product_qty,
                    'qty_done': move.qty_done,
                    'transfer_qty': [],
                    'lot_dest_id': [],
                })
        # add too available stock in location_id
        # to be able to transfer more than the reserved amount if necessary
        for prod in picking_product_ids:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', prod),
                ('location_id', '=', self.location_id.id)
            ])
            for quant in quants:
                qty_available = quant['quantity'] - quant['reserved_quantity']
                if float_compare(qty_available, 0, precision_digits=pd) > 0:
                    reg_found = False
                    for reg in grouped_by_lot:
                        if reg['product_id'] == quant.product_id.id \
                                and reg['lot_id'] == quant.lot_id.id:
                            reg['product_qty'] += qty_available
                            reg_found = True
                    if not reg_found:
                        grouped_by_lot.append({
                            'product_id': quant.product_id.id,
                            'product_uom_id': quant.product_uom_id.id,
                            'lot_id': quant.lot_id.id,
                            'product_qty': qty_available,
                            'qty_done': 0,
                            'transfer_qty': [],
                            'lot_dest_id': [],
                        })
        # how many is detailed by product and lot
        # and we need to create stock for this lot
        nosuggest_lots = list(
            filter(lambda x:
                   not float_is_zero(x['qty_done'], precision_digits=pd)
                   and float_is_zero(x['product_qty'], precision_digits=pd),
                   grouped_by_lot)
        )
        reserved_lot = list(
            filter(lambda x:
                   float_is_zero(x['qty_done'], precision_digits=pd),
                   grouped_by_lot)
        )
        # if there is no reserved moves: nothing to do
        if len(reserved_lot) == 0:
            return []
        # 1.- review the lots that have nothing reserved
        for lot in nosuggest_lots:
            qty_done = lot['qty_done']
            qty_available = 0
            for reg in reserved_lot:
                if reg['product_id'] == lot['product_id'] \
                        and float_compare(qty_done, 0,
                                          precision_digits=pd) > 0 \
                        and float_compare(reg['product_qty'],
                                          sum(reg['transfer_qty']),
                                          precision_digits=pd) > 0:
                    qty_available += reg['product_qty']
                    diff = reg['product_qty'] - sum(reg['transfer_qty'])
                    if float_compare(diff,
                                     qty_done,
                                     precision_digits=pd) >= 0:
                        reg['transfer_qty'].append(qty_done)
                        reg['lot_dest_id'].append(lot['lot_id'])
                        qty_done = 0
                        break
                    else:
                        reg['transfer_qty'].append(diff)
                        reg['lot_dest_id'].append(lot['lot_id'])
                        qty_done -= diff
            if float_compare(qty_done, 0, precision_digits=pd) > 0:
                prod = self.env["product.product"].browse(lot['product_id'])
                raise UserError(_("Not enough stock for product %s"
                                  " (necessary %.1f, available %.1f)")
                                % (prod.name, lot['qty_done'], qty_available))
        # return transfer to do
        transfer_lot = list(
            filter(lambda x:
                   not float_is_zero(sum(x['transfer_qty']),
                                     precision_digits=pd),
                   grouped_by_lot)
        )
        return transfer_lot

    def _prepare_move_origin_values(self, lot):
        return {
            'name': _('%s - Transfer') % self.name,
            'product_id': lot['product_id'],
            'product_uom': lot['product_uom_id'],
            'product_uom_qty': sum(lot['transfer_qty']),
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': self.location_id.id,
            'location_dest_id': self.partner_id.property_stock_customer.id,
            'move_line_ids': [(0, 0, {
                'product_id': lot['product_id'],
                'product_uom_id': lot['product_uom_id'],
                'qty_done': sum(lot['transfer_qty']),
                'location_id': self.location_id.id,
                'location_dest_id': self.partner_id.property_stock_customer.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': lot['lot_id'],
                'owner_id': self.owner_id.id,
            })]
        }

    def _prepare_move_dest_values(self, lot):
        move_lines = []
        for index in range(len(lot['lot_dest_id'])):
            move_lines.append((0, 0, {
                'product_id': lot['product_id'],
                'product_uom_id': lot['product_uom_id'],
                'qty_done': lot['transfer_qty'][index],
                'location_id': self.partner_id.property_stock_customer.id,
                'location_dest_id': self.location_id.id,
                'company_id': self.company_id.id or self.env.company.id,
                'lot_id': lot['lot_dest_id'][index],
                'owner_id': self.owner_id.id,
            }))
        return {
            'name': _('%s - Transfer') % self.name,
            'product_id': lot['product_id'],
            'product_uom': lot['product_uom_id'],
            'product_uom_qty': sum(lot['transfer_qty']),
            'company_id': self.company_id.id or self.env.company.id,
            'state': 'confirmed',
            'location_id': self.partner_id.property_stock_customer.id,
            'location_dest_id': self.location_id.id,
            'move_line_ids': move_lines,
        }

    def _create_intermediate_transfers(self):
        """
        check if we have to create transfer from origin to intermediate location
            and then generate movement from intermediate location
        """
        transfer_lot = self._review_intermediate_transfers()
        for lot in transfer_lot:
            # move from origin lot to transfer location
            move = self.env['stock.move'].with_context(
                inventory_mode=False).create(
                self._prepare_move_origin_values(lot))
            move._action_done()
            # move lot from transfer location to dest
            move = self.env['stock.move'].with_context(
                inventory_mode=False).create(
                self._prepare_move_dest_values(lot))
            move._action_done()

    def button_validate(self):

        if self.picking_type_id.auto_create_lot:
            for line in self.move_line_ids.filtered(
                lambda x: (
                    not x.lot_id
                    and not x.lot_name
                    and x.product_id.tracking != "none"
                    and x.product_id.auto_create_lot
                )
            ):
                production_lot = line.create_lot_product_supplier_date_eco()
                line.lot_id = production_lot.id
                line.lot_name = production_lot.name

        if self.picking_type_id.auto_create_lot \
                and self.location_id.usage == "internal" \
                and self.location_dest_id.usage == "internal":
            self._create_intermediate_transfers()

        return super().button_validate()
