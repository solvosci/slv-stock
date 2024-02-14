# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, api


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"    
    
    def name_get(self):
        context = self.env.context
        if context.get('stock_barcodes_advanced', False):
            result = []
            for lot in self:
                name = "%s (%.2f %s)" % (
                    lot.name, lot.product_qty, lot.product_uom_id.name
                )
                result.append((lot.id, name))
            return result
        else:
            return super().name_get()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        context = self.env.context
        if context.get('stock_barcodes_advanced', False):
            domain = args or []
            domain += [("name", operator, name)]
            return self.search(domain).sorted(key=lambda x: x.product_qty, reverse=True).name_get()

        return super().name_search(name=name, args=args, operator=operator, limit=limit)
