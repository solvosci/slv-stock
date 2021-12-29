# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields
from odoo.tools.float_utils import float_round


class ProductProduct(models.Model):
    _inherit = 'product.product'

    expected_qty = fields.Float(
        'Expected Quantity', compute='_compute_quantities',
        digits='Product Unit of Measure', compute_sudo=False)

    def _compute_quantities(self):
        super()._compute_quantities()
        products = self.filtered(lambda p: p.type != 'service')
        res = products._compute_quantities_dict(self._context.get('lot_id'), self._context.get('owner_id'), self._context.get('package_id'), self._context.get('from_date'), self._context.get('to_date'))
        for product in products:
            product.expected_qty = res[product.id]['expected_qty']

        services = self - products
        services.expected_qty = 0.0

    def _compute_quantities_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        res = super()._compute_quantities_dict(lot_id, owner_id, package_id, from_date, to_date)

        for product in self.with_context(prefetch_fields=False):
            product_id = product.id
            rounding = product.uom_id.rounding
            domain_move = [
                ("product_id", "=", product_id),
                ("purchase_line_id.related_real_order_id", "!=", False),
            ]
            domain_pol = [
                ("product_id", "=", product_id),
                ("related_real_order_id", "!=", False),
                ("order_id.state", "=", "cancel")
            ]

            classified_qty = sum(self.env["stock.move"].search(domain_move).mapped('product_uom_qty'))
            cancelled_qty = sum(self.env["purchase.order.line"].search(domain_pol).mapped('product_uom_qty'))
            expected_qty = res[product_id]['virtual_available'] - classified_qty - cancelled_qty
            res[product_id]['expected_qty'] = float_round(expected_qty, precision_rounding=rounding)

        return res

    def action_product_expected_report(self):
        action = self.env.ref('stock_picking_mgmt_weight.report_stock_quantity_action').read()[0]
        action['domain'] = [
            ('product_id', '=', self.id),
            ('warehouse_id', '!=', False),
        ]
        return action
