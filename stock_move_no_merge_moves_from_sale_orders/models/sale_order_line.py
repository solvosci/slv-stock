# © 2025 Solvos Consultoría Informática (http://www.solvos.es)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        return super(SaleOrderLine, self.with_context(from_sale_order=True))._action_launch_stock_rule(previous_product_uom_qty=previous_product_uom_qty)
