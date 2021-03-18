# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare, float_is_zero
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        result = super()._action_confirm()
        for order in self:
            order.order_line.sudo()._purchase_distribution_generation()
        return result

    def _activity_cancel_on_purchase(self):
        """ If some SO are cancelled,
            if purchase line state is draft, we can delete it
            else we need to put an activity in PO
            If sale lines of different sale orders impact different purchase,
            we only want one activity to be attached.
        """
        po_lines = self.env['purchase.order.line'].search([
            ('sale_line_id', 'in', self.mapped('order_line').ids)
        ])
        po_to_notify_map=po_lines.review_relative_line_purchase(self.name, self.id)
        # put an activity in PO
        for purchase_order, sale_order_lines in po_to_notify_map.items():
            purchase_order.activity_schedule_with_view(
                'mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid='sale_purchase.exception_purchase_on_sale_cancellation',
                render_context={
                    'sale_orders': sale_order_lines.mapped('order_id'),
                    'sale_order_lines': sale_order_lines,
                })

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _purchase_modif_ordered_qty(self, new_qty, origin_values):
        """ Modify the quantity from SO line will
            redo the purchase order lines (deleting existing if possible)
            or add a next acitivities on the related purchase order
            :param new_qty: new quantity
            :param origin_values: map from sale line id to old value
        """
        po_to_notify_map = {}  # map PO -> recordset of SOL
        # First delete PO if all po lines are in draft
        for so_line in self:
            po_lines = self.env['purchase.order.line'].search([
                ('sale_line_id', '=', so_line.id),
            ])
            po_lines_confirmed = po_lines.filtered(
                lambda r: r.state in ('purchase', 'done')
            )
            if po_lines_confirmed:
                for po_line in po_lines.filtered(
                        lambda r: r.state != 'cancel'):
                    po_to_notify_map.setdefault(
                        po_line.order_id,
                        self.env['sale.order.line']
                    )
                    po_to_notify_map[po_line.order_id] |= po_line.sale_line_id
            else:
                po_lines.review_relative_line_purchase(
                    so_line.order_id.name, so_line.order_id.id)
        # put an activity in PO
        for purchase_order, sale_order_lines in po_to_notify_map.items():
            render_context = {
                'sale_lines': sale_order_lines,
                'sale_orders': sale_order_lines.mapped('order_id'),
                'origin_values': origin_values,
            }
            purchase_order.activity_schedule_with_view(
                'mail.mail_activity_data_warning',
                user_id=purchase_order.user_id.id or self.env.uid,
                views_or_xmlid='sale_purchase_according_declared_stock'
                               '.exception_purchase_on_sale_quantity_changed',
                render_context=render_context)

    @api.model_create_multi
    def create(self, values):
        lines = super(SaleOrderLine, self).create(values)
        # Generate purchase when SO line don't have purchase line
        lines.filtered(
            lambda line: line.state == 'sale' and not line.purchase_line_count
        )._purchase_distribution_generation()
        return lines

    """
    It is not possible to delete an order line in a state already confirmed.
    def unlink(self):
        po_lines = self.env['purchase.order.line'].search([
            ('sale_line_id', '=', self.id),
            ('state', '!=', 'cancel')
        ])
        po_to_notify_map=po_lines.review_relative_line_purchase()
        return super(SaleOrderLine, self).unlink()
    """

    def write(self, values):
        modif_lines = None
        modif_vals = {}
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].\
                precision_get('Product Unit of Measure')
            modif_lines = self.sudo().filtered(
                lambda r: r.purchase_line_count
                and float_compare(r.product_uom_qty,
                                  values['product_uom_qty'],
                                  precision_digits=precision) != 0
            )
            modif_vals = {line.id: line.product_uom_qty for line in modif_lines}

            result = super(SaleOrderLine, self).write(values)

            if modif_lines:
                modif_lines._purchase_modif_ordered_qty(
                    values['product_uom_qty'], modif_vals)
                # Generate purchase when SO line don't have purchase line
                self.sudo().filtered(
                    lambda
                        line: line.state == 'sale' and not line.purchase_line_count
                )._purchase_distribution_generation()

            return result

    def _purchase_distribution_prepare_order_values(self, supplier):
        """ Returns values to create purchase order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        fiscal_position = self.env['account.fiscal.position']
        fpos = fiscal_position.sudo().get_fiscal_position(supplier.id)
        payment_term_id = supplier.property_supplier_payment_term_id.id
        currency_id = supplier.property_purchase_currency_id.id \
                      or self.env.company.currency_id.id
        return {
            'partner_id': supplier.id,
            'partner_ref': supplier.ref,
            'company_id': self.company_id.id,
            'currency_id': currency_id,
            'origin': self.order_id.name,
            'payment_term_id': payment_term_id,
            'date_order': datetime.today(),
            'fiscal_position_id': fpos,
        }

    def _purchase_distribution_prepare_line_values(
            self, po, supplierinfo=False, quantity=False):
        """ Returns the values to create the PO line from the current SO line.
            :param po: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line
        """
        self.ensure_one()
        pd = self.env['decimal.precision'].precision_get(
            'Product Unit of Measure')
        # compute quantity from SO line UoM
        product_quantity = quantity or self.product_uom_qty

        purchase_qty_uom = self.product_uom._compute_quantity(
            product_quantity, self.product_id.uom_po_id)

        fpos = po.fiscal_position_id
        tax = fpos.map_tax(self.product_id.supplier_taxes_id) \
            if fpos else self.product_id.supplier_taxes_id
        if tax:
            tax = tax.filtered(lambda t: t.company_id.id == self.company_id.id)

        price = 0.0
        seller = self.product_id._select_seller(
            partner_id=po.partner_id,
            quantity=purchase_qty_uom,
            date=po.date_order and po.date_order.date(),
            uom_id=self.product_id.uom_po_id
        )
        price = seller.price
        if float_compare(price, 0, precision_digits=pd) == 0:
            price = self.product_id.standard_price
        if float_compare(price, 0, precision_digits=pd) != 0:
            account_tax = self.env['account.tax']
            price = account_tax.sudo()._fix_tax_included_price_company(
                price,
                self.product_id.supplier_taxes_id,
                tax,
                self.company_id)
            if seller and po.currency_id \
                    and seller.currency_id != po.currency_id:
                price = seller.currency_id.compute(price,po.currency_id)

        moves_rel = self.move_ids.filtered(
            lambda z: z.state not in ('done', 'cancel'))
        for move in moves_rel:
            move.write({
               # 'procure_method': 'make_to_stock',
                'state': 'waiting',
                'delay_alert': False,
            })

        return {
            'name': '[%s] %s - %s - %s' %
                    (self.product_id.default_code, self.product_id.name,
                     self.order_id.name, self.order_id.partner_id.name),
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price,
            'propagate_cancel': False,
            'date_planned': po.date_order
                            + relativedelta(days=int(seller.delay)),
            'taxes_id': [(6, 0, tax.ids)],
            'order_id': po.id,
            'sale_line_id': self.id,
            'move_dest_ids': [(4, x.id) for x in moves_rel],
        }

    def _select_distribution_seller(self):
        self.ensure_one()

        res = []
        sellers = self.env['res.partner'].search([
            ('property_stock_supplier.usage', '=', 'internal')
        ])
        # 1.- calculations by warehouse
        warehouse_data = []
        for seller in sellers:
            obj_purchase = self.env['purchase.order.line'].search([
                ('order_id.partner_id', '=', seller.id),
                ('order_id.state', '=', 'draft'),
                ('product_id', '=', self.product_id.id),
            ])
            purchase_qty = sum(obj_purchase.mapped("product_qty"))
            reg_found = False
            for reg in warehouse_data:
                if reg['warehouse'] == seller.property_stock_supplier.id:
                    reg['sharers'] += 1
                    reg['purchase_qty'] += purchase_qty
                    reg_found = True
            if not reg_found:
                stock_qty = self.env['stock.quant']._get_available_quantity(
                    self.product_id, seller.property_stock_supplier
                )
                warehouse_data.append({
                    'warehouse': seller.property_stock_supplier.id,
                    'sharers': 1,
                    'stock_qty': stock_qty,
                    'purchase_qty': purchase_qty,
                    'distributed_qty': 0,
                })
        # 2.- calculation by seller: the way to not lose the remains
        for reg in warehouse_data:
            available_qty = reg['stock_qty'] - reg['purchase_qty']
            sharers = reg['sharers']
            if float_compare(available_qty, 0, precision_digits=1) <= 0:
                continue
            shared_number = 0
            for seller in sellers.filtered(
                    lambda x: x.property_stock_supplier.id == reg['warehouse']):
                shared_number += 1
                seller_qty = available_qty / sharers
                if shared_number == sharers:
                    # last shared: keeps with the remains
                    # TODO: See if we can find a way to assign the difference, (in order to equalize ..)
                    #   to the partner who has the least amount in purchases for that product in the month
                    seller_qty = available_qty - reg['distributed_qty']
                if float_compare(seller_qty, round(seller_qty, 1),
                                 precision_digits=1) <= 0:
                    seller_qty = round(seller_qty, 1)
                else:
                    seller_qty = round(seller_qty, 1) - 0.1
                reg['distributed_qty'] += seller_qty
                if float_compare(seller_qty, 0, precision_digits=1) > 0:
                    res.append({
                        'seller': seller,
                        'available_qty': seller_qty,
                        'po_line_qty': 0
                    })
        return res

    def _purchase_distribution_create(self, quantity=False):
        """ On Sales Order confirmation,
            all lines can create purchase order lines and a purchase order.
            If a line should create a RFQ, it will check for existing PO.
            If no one is find, SO line will create one, then adds a new PO line.
            The created purchase order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line
        """
        PurchaseOrder = self.env['purchase.order']
        PurchaseOrderLine = self.env['purchase.order.line']
        supplier_po_map = {}
        sale_line_purchase_map = {}
        for line in self:
            line = line.with_context(force_company=line.company_id.id)
            so_line_qty = round(line.product_uom_qty, 1)
            if float_compare(so_line_qty, line.product_uom_qty,
                             precision_digits=1) != 0:
                raise UserError(
                    _("Quantity ordered in product %s "
                      "has too many decimal places")
                    % (line.product_id.display_name,))
            reserved_moves = self.env['stock.move'].search([
                ('sale_line_id', '=', self.id),
                ('state', '!=', 'cancel'),
            ])
            # check if there is something reserved
            reserv_qty = sum(item.reserved_availability for item in reserved_moves)
            if float_compare(reserv_qty, so_line_qty, precision_digits=1) >= 0:
                continue
            so_line_qty = round(so_line_qty - reserv_qty, 1)
            # determine vendor of the order
            suppliers = line._select_distribution_seller()
            if len(suppliers) == 0:
                raise UserError(
                    _("There is no vendor with stock for product %s")
                    % (line.product_id.display_name,))
            total_available_qty = 0
            for supplier in suppliers:
                total_available_qty += supplier["available_qty"]
            if float_compare(so_line_qty,
                             total_available_qty,
                             precision_digits=1) > 0:
                raise UserError(
                    _("There is not enough stock for product "
                      "%s (necessary %.1f, available %.1f)")
                    % (line.product_id.display_name, so_line_qty,
                       total_available_qty))
            #calculate the amount allocated to each supplier
            total_po_line_qty = 0
            suppliers_in_distrib = len(suppliers)
            qty_in_distrib = so_line_qty
            sort_suppliers = sorted(suppliers, key=lambda x: x['available_qty'])
            for supplier in sort_suppliers:
                po_line_qty = round(qty_in_distrib/suppliers_in_distrib, 1)
                if float_compare(po_line_qty,
                                 supplier["available_qty"],
                                 precision_digits=1) > 0:
                    po_line_qty = round(supplier["available_qty"], 1)
                supplier["po_line_qty"] = po_line_qty
                qty_in_distrib -= po_line_qty
                suppliers_in_distrib -= 1
                total_po_line_qty += po_line_qty
            diff = float_compare(total_po_line_qty,
                                 so_line_qty,
                                 precision_digits=1)
            if diff != 0:
                # TODO: See if we can find a way to assign the difference, (in order to equalize ..)
                #   if it is positive to the partner who has the least amount in purchases for that product in the month
                #   and if it is negative to the one who has more purchases
                for supplier in suppliers:
                    diff = float_compare(total_po_line_qty,
                                         so_line_qty,
                                         precision_digits=1)
                    if diff > 0:
                        supplier["po_line_qty"] -= 0.1
                        total_po_line_qty -= 0.1
                    if diff < 0:
                        if float_compare(supplier["available_qty"],
                                         supplier["po_line_qty"],
                                         precision_digits=1) > 0:
                            supplier["po_line_qty"] += 0.1
                            total_po_line_qty += 0.1

            for supplier in suppliers:
                if float_is_zero(supplier["po_line_qty"], precision_digits=1):
                    continue

                partner_supplier = supplier["seller"]

                # determine (or create) PO
                purchase_order = supplier_po_map.get(partner_supplier.id)
                if not purchase_order:
                    purchase_order = PurchaseOrder.search([
                        ('partner_id', '=', partner_supplier.id),
                        ('state', '=', 'draft'),
                    ], limit=1)
                if not purchase_order:
                    values = line._purchase_distribution_prepare_order_values(
                        partner_supplier
                    )
                    purchase_order = PurchaseOrder.create(values)
                else:  # update origin of existing PO
                    so_name = line.order_id.name
                    origins = []
                    if purchase_order.origin:
                        origins = purchase_order.origin.split(', ') + origins
                    if so_name not in origins:
                        origins += [so_name]
                        purchase_order.write({
                            'origin': ', '.join(origins)
                        })
                supplier_po_map[partner_supplier.id] = purchase_order

                # add a PO line to the PO
                values = line._purchase_distribution_prepare_line_values(
                    purchase_order, partner_supplier,
                    quantity=supplier["po_line_qty"]
                )
                purchase_line = PurchaseOrderLine.create(values)

                # link the generated purchase to the SO line
                sale_line_purchase_map.setdefault(
                    line, line.env['purchase.order.line']
                )
                sale_line_purchase_map[line] |= purchase_line
        return sale_line_purchase_map

    def _purchase_distribution_generation(self):
        """ Create a Purchase for the first time from the sale line.
            If SO line already created a PO, it will not create a second one.
        """
        sale_line_purchase_map = {}
        for line in self:
            # Do not regenerate PO line if the SO line has already created
            if not line.purchase_line_count:
                result = line._purchase_distribution_create()
                sale_line_purchase_map.update(result)
        return sale_line_purchase_map
