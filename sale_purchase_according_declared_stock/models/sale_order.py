# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    picking_status = fields.Text(string='Picking Status',
                                 compute='_compute_picking_status',
                                 store=True)

    # TODO: check if we have to do something different than what is done in sale_purchase when the sale is canceled or modified
    @api.depends('picking_ids.state')
    def _compute_picking_status(self):
        # maybe we want to buy:  https://apps.odoo.com/apps/modules/13.0/cit_sale_delivery_status/
        # TODO: improve status text (with description) instead of with code. would it be enough to see only the status of the last picking_id?
        for order in self:
            status_text = []
            for item in order.picking_ids:
                if item.state not in status_text:
                    status_text += [item.state]
            order.picking_status = ', '.join(status_text)

    def _action_confirm(self):
        result = super()._action_confirm()
        for order in self:
            order.order_line.sudo()._purchase_distribution_generation()
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # TODO: check if we need to do something different than what is done in sale_purchase when modifying a sale line
    # TODO: we really have to check: _onchange_service_product_uom_qty, _purchase_increase_ordered_qty...¿create? ¿write?
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
        if seller:
            account_tax = self.env['account.tax']
            price = account_tax.sudo()._fix_tax_included_price_company(
                seller.price,
                self.product_id.supplier_taxes_id,
                tax,
                self.company_id)
            if po.currency_id and seller.currency_id != po.currency_id:
                price = seller.currency_id.compute(price,po.currency_id)

        for move in self.move_ids:
            move.write({
                'procure_method': 'make_to_order',
                'state': 'waiting',
                'delay_alert': False,
            })

        return {
            'name': '[%s] %s - %s %s - %s' %
                    (self.product_id.default_code, self.product_id.name,
                     _("order"),
                     self.order_id.name, self.order_id.partner_id.name),
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price,
            'date_planned': po.date_order
                            + relativedelta(days=int(seller.delay)),
            'taxes_id': [(6, 0, tax.ids)],
            'order_id': po.id,
            'sale_line_id': self.id,
            'move_dest_ids': [(4, x.id) for x in self.move_ids],
        }

    def _select_distribution_seller(self):
        self.ensure_one()

        res = []
        sellers = self.env['res.partner'].search([
            ('property_stock_supplier.usage', '=', 'internal')
        ])
        for seller in sellers:
            stock_qty = self.env['stock.quant']._get_available_quantity(
                self.product_id, seller.property_stock_supplier
            )
            obj_purchase = self.env['purchase.order.line'].search([
                ('order_id.partner_id', '=', seller.id),
                ('order_id.state', '=', 'draft'),
                ('product_id', '=', self.product_id.id),
            ])
            purchase_qty = sum(obj_purchase.mapped("product_qty"))
            available_qty = stock_qty - purchase_qty
            if not available_qty or available_qty <= 0:
                continue
            res.append({
                'seller': seller,
                'available_qty': available_qty,
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
            stock_move = self.env['stock.move'].search([
                ('sale_line_id', '=', self.id),
                ('state', '!=', 'cancel'),
            ])
            # TODO: See if we are reserving stock that came in for another order!!
            reserv_qty = sum(item.reserved_availability for item in stock_move)
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
            for supplier in suppliers:
                coefficient = supplier["available_qty"] / total_available_qty
                po_line_qty = round(so_line_qty * coefficient, 1)
                while float_compare(po_line_qty,
                                    supplier["available_qty"],
                                    precision_digits=1) > 0:
                    po_line_qty -= 0.1
                supplier["po_line_qty"] = po_line_qty
                total_po_line_qty += po_line_qty
            diff = float_compare(total_po_line_qty,
                                 so_line_qty,
                                 precision_digits=1)
            if diff != 0:
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
