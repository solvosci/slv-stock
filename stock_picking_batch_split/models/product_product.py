# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        context = self.env.context
        if context.get('stock_picking_batch_split', False):
            product_batch_ids = self.env['stock.picking.batch'].browse(context.get('stock_picking_batch_split')).move_lines.mapped('product_id')
            domain = args or []
            domain += ['&', ("name", operator, name), ('id', 'in', product_batch_ids.ids)]
            return self.search(domain).name_get()

        return super().name_search(name=name, args=args, operator=operator, limit=limit)
