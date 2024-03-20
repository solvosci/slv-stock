# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    qty_remaining_not_done = fields.Float(compute='_compute_qty_not_done')

    def _compute_qty_not_done(self):
        for record in self:
            qty_not_done = sum(self.env['stock.move.line'].search([
                ('product_id', '=', record.product_id.id),
                ('lot_id', '=', record.id),
                ('state', 'not in', ['done', 'cancel']),
                ('location_dest_id.usage', '!=', 'interanl'),
            ]).mapped('qty_done'))
            record.qty_remaining_not_done = record.product_qty - qty_not_done

    def name_get(self):
        context = self.env.context
        if context.get('stock_picking_assigned', False):
            result = []
            for lot in self:
                name = "%s (%.2f %s)" % (
                    lot.name, lot.qty_remaining_not_done, lot.product_uom_id.name
                )
                result.append((lot.id, name))
            return result
        else:
            return super().name_get()

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        context = self.env.context
        if context.get('stock_picking_assigned', False):
            domain = args or []
            domain += [("name", operator, name)]
            return self.search(domain).sorted(key=lambda x: x.qty_remaining_not_done, reverse=True).name_get()

        return super().name_search(name=name, args=args, operator=operator, limit=limit)

