# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _action_confirm(self):
        result = super(SaleOrder, self)._action_confirm()
        for order in self:
            order.order_line.sudo()._purchase_distribution_generation()
        return result


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.model_create_multi
    def create(self, values):
        lines = super(SaleOrderLine, self).create(values)
        # Do not generate purchase when expense SO line since the product is already delivered
        lines.filtered(
            lambda line: line.state == 'sale' and not line.is_expense
        )._purchase_distribution_generation()
        return lines

    def write(self, values):
        increased_lines = None
        decreased_lines = None
        increased_values = {}
        decreased_values = {}
        if 'product_uom_qty' in values:
            precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            increased_lines = self.sudo().filtered(lambda r: r.purchase_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == -1)
            decreased_lines = self.sudo().filtered(lambda r: r.purchase_line_count and float_compare(r.product_uom_qty, values['product_uom_qty'], precision_digits=precision) == 1)
            increased_values = {line.id: line.product_uom_qty for line in increased_lines}
            decreased_values = {line.id: line.product_uom_qty for line in decreased_lines}

        result = super(SaleOrderLine, self).write(values)

        if increased_lines:
            increased_lines._purchase_increase_ordered_qty(values['product_uom_qty'], increased_values)
        if decreased_lines:
            decreased_lines._purchase_decrease_ordered_qty(values['product_uom_qty'], decreased_values)
        return result

    def _purchase_increase_ordered_qty(self, new_qty, origin_values):
        """ Increase the quantity on the related purchase lines
            :param new_qty: new quantity (higher than the current one on SO line), expressed
                in UoM of SO line.
            :param origin_values: map from sale line id to old value for the ordered quantity (dict)
        """
        for line in self:
            last_purchase_line = self.env['purchase.order.line'].search([('sale_line_id', '=', line.id)], order='create_date DESC', limit=1)
            if last_purchase_line.state in ['draft', 'sent', 'to approve']:  # update qty for draft PO lines
                quantity = line.product_uom._compute_quantity(new_qty, last_purchase_line.product_uom)
                last_purchase_line.write({'product_qty': quantity})
            elif last_purchase_line.state in ['purchase', 'done', 'cancel']:  # create new PO, by forcing the quantity as the difference from SO line
                quantity = line.product_uom._compute_quantity(new_qty - origin_values.get(line.id, 0.0), last_purchase_line.product_uom)
                line._purchase_distribution_generation(quantity=quantity)

    def _purchase_distribution_prepare_order_values(self, supplierinfo):
        """ Returns the values to create the purchase order from the current SO line.
            :param supplierinfo: record of product.supplierinfo
            :rtype: dict
        """
        self.ensure_one()
        partner_supplier = supplierinfo.name
        fiscal_position_id = self.env['account.fiscal.position'].sudo().get_fiscal_position(partner_supplier.id)
        date_order = self._purchase_get_date_order(supplierinfo)
        return {
            'partner_id': partner_supplier.id,
            'partner_ref': partner_supplier.ref,
            'company_id': self.company_id.id,
            'currency_id': partner_supplier.property_purchase_currency_id.id or self.env.company.currency_id.id,
            'dest_address_id': False, # False since only supported in stock
            'origin': self.order_id.name,
            'payment_term_id': partner_supplier.property_supplier_payment_term_id.id,
            'date_order': date_order,
            'fiscal_position_id': fiscal_position_id,
        }

    def _purchase_distribution_prepare_line_values(self, purchase_order, supplierinfo=False, quantity=False):
        """ Returns the values to create the purchase order line from the current SO line.
            :param purchase_order: record of purchase.order
            :rtype: dict
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        self.ensure_one()
        # compute quantity from SO line UoM
        product_quantity = self.product_uom_qty
        if quantity:
            product_quantity = quantity

        purchase_qty_uom = self.product_uom._compute_quantity(product_quantity, self.product_id.uom_po_id)

        fpos = purchase_order.fiscal_position_id
        taxes = fpos.map_tax(self.product_id.supplier_taxes_id) if fpos else self.product_id.supplier_taxes_id
        if taxes:
            taxes = taxes.filtered(lambda t: t.company_id.id == self.company_id.id)

        # compute unit price
        price_unit = 0.0
        if supplierinfo:
            price_unit = self.env['account.tax'].sudo()._fix_tax_included_price_company(supplierinfo.price, self.product_id.supplier_taxes_id, taxes, self.company_id)
            if purchase_order.currency_id and supplierinfo.currency_id != purchase_order.currency_id:
                price_unit = supplierinfo.currency_id.compute(price_unit, purchase_order.currency_id)

        # purchase line description in supplier lang
        product_in_supplier_lang = self.product_id.with_context(
            lang=supplierinfo.name.lang,
            partner_id=supplierinfo.name.id,
        )
        name = '[%s] %s' % (self.product_id.default_code, product_in_supplier_lang.display_name)
        if product_in_supplier_lang.description_purchase:
            name += '\n' + product_in_supplier_lang.description_purchase

        return {
            'name': '[%s] %s' % (self.product_id.default_code, self.name) if self.product_id.default_code else self.name,
            'product_qty': purchase_qty_uom,
            'product_id': self.product_id.id,
            'product_uom': self.product_id.uom_po_id.id,
            'price_unit': price_unit,
            'date_planned': fields.Date.from_string(purchase_order.date_order) + relativedelta(days=int(supplierinfo.delay)),
            'taxes_id': [(6, 0, taxes.ids)],
            'order_id': purchase_order.id,
            'sale_line_id': self.id,
        }

    def _select_distribution_seller(self, quantity=0.0, uom_id=False, params=False):
        self.ensure_one()
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        res = self.env['res.partner']
        sellers = self.env['res.partner'].search([('property_stock_supplier.id', '!=', False)])
        if self.env.context.get('force_company'):
            sellers = sellers.filtered(lambda s: not s.company_id or s.company_id.id == self.env.context['force_company'])
        for seller in sellers:

            available_qty = self.env['stock.quant']._get_available_quantity(self.product_id.id,
                                                            seller.property_stock_supplier)
            if not available_qty or available_qty <= 0:
                continue
            if not res or res.name == seller.name:
                res |= seller

        return res[:1]

    def _purchase_distribution_create(self, quantity=False):
        """ On Sales Order confirmation, all lines can create a purchase order line and maybe a purchase order.
            If a line should create a RFQ, it will check for existing PO. If no one is find, the SO line will create one, then adds
            a new PO line. The created purchase order line will be linked to the SO line.
            :param quantity: the quantity to force on the PO line, expressed in SO line UoM
        """
        PurchaseOrder = self.env['purchase.order']
        supplier_po_map = {}
        sale_line_purchase_map = {}
        for line in self:
            line = line.with_context(force_company=line.company_id.id)
            # determine vendor of the order (take the first matching company and product)
            suppliers = line._select_distribution_seller(
                quantity=line.product_uom_qty, uom_id=line.product_uom)
            if not suppliers:
                raise UserError(_("There is no vendor whith stock for this product.") % (line.product_id.display_name,))
            supplierinfo = suppliers[0]
            partner_supplier = supplierinfo.name  # yes, this field is not explicit .... it is a res.partner !

            # determine (or create) PO
            purchase_order = supplier_po_map.get(partner_supplier.id)
            if not purchase_order:
                purchase_order = PurchaseOrder.search([
                    ('partner_id', '=', partner_supplier.id),
                    ('state', '=', 'draft'),
                    ('company_id', '=', line.company_id.id),
                ], limit=1)
            if not purchase_order:
                values = line._purchase_distribution_prepare_order_values(supplierinfo)
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
            values = line._purchase_distribution_prepare_line_values(purchase_order, partner_supplier, quantity=quantity)
            purchase_line = line.env['purchase.order.line'].create(values)

            # link the generated purchase to the SO line
            sale_line_purchase_map.setdefault(line, line.env['purchase.order.line'])
            sale_line_purchase_map[line] |= purchase_line

        return sale_line_purchase_map

    def _purchase_distribution_generation(self):
        """ Create a Purchase for the first time from the sale line. If the SO line already created a PO, it
            will not create a second one.
        """
        sale_line_purchase_map = {}
        for line in self:
            # Do not regenerate PO line if the SO line has already created one in the past (SO cancel/reconfirmation case)
            if not line.purchase_line_count:
                result = line._purchase_distribution_create()
                sale_line_purchase_map.update(result)
        return sale_line_purchase_map
