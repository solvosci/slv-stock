# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields, api
from datetime import datetime, timedelta


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    exclude_in_assignments = fields.Boolean()
    qty_remaining_not_done = fields.Float(compute='_compute_qty_not_done')

    # TODO: Revisar tema cantidades reservadas
    def _compute_qty_not_done(self):
        context = self.env.context
        for record in self:
            if context.get('location_id', False):
                location_id = self.env['stock.location'].browse(int(context.get('location_id'))).id
                qty_not_done = sum(self.env['stock.move.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('lot_id', '=', record.id),
                    ('qty_done', '>', 0),
                    ('state', 'not in', ['done', 'cancel']),
                    ('location_id', '=', location_id),
                    # ('location_dest_id.usage', '!=', 'internal'),
                ]).mapped('qty_done'))

                qty = sum(self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('lot_id', '=', record.id),
                    ('location_id', '=', location_id),
                ]).mapped('quantity'))
                record.qty_remaining_not_done = qty - qty_not_done
            else:
                qty_not_done = sum(self.env['stock.move.line'].search([
                    ('product_id', '=', record.product_id.id),
                    ('lot_id', '=', record.id),
                    ('state', 'not in', ['done', 'cancel']),
                    ('location_dest_id.usage', '!=', 'internal'),
                ]).mapped('qty_done'))

                record.qty_remaining_not_done = record.product_qty - qty_not_done

    def name_get(self):
        context = self.env.context
        if context.get('stock_picking_assigned', False):
            result = []
            for lot in self:
                if lot.qty_remaining_not_done > 0:
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
            domain += ['&', ("name", operator, name), ('exclude_in_assignments', '=', False)]
            return self.search(domain).sorted(key=lambda x: x.qty_remaining_not_done, reverse=True).name_get()
        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    @api.model
    def cron_exclude_old_records(self):
        lot_ids = self.search([('exclude_in_assignments', '=', False)])
        lot_ids.filtered(lambda x: x.qty_remaining_not_done <= 0).write({'exclude_in_assignments': True})
