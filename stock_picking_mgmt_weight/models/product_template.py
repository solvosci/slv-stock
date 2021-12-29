# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expected_qty = fields.Float(
        'Expected Quantity', compute='_compute_quantities',
        digits='Product Unit of Measure', compute_sudo=False)

    def _compute_quantities(self):
        super()._compute_quantities()
        res = self._compute_quantities_dict()
        for template in self:
            template.expected_qty = res[template.id]['expected_qty']

    def _compute_quantities_dict(self):
        res = super()._compute_quantities_dict()

        for template in self:
            domain_move = [
                ("purchase_line_id.product_id.product_tmpl_id", "=", template.id),
                ("purchase_line_id.related_real_order_id", "!=", False),
            ]
            domain_pol = [
                ("product_id.product_tmpl_id", "=", template.id),
                ("related_real_order_id", "!=", False),
                ("order_id.state", "=", "cancel")
            ]

            classified_qty = sum(self.env["stock.move"].search(domain_move).mapped('product_uom_qty'))
            cancelled_qty = sum(self.env["purchase.order.line"].search(domain_pol).mapped('product_uom_qty'))
            expected_qty = res[template.id]['virtual_available'] - classified_qty - cancelled_qty

            res[template.id]["expected_qty"] = expected_qty

        return res
