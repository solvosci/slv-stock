# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
import time
from odoo import models, fields, api
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class Picking(models.Model):
    _inherit = "stock.picking"

    scheduled_date_very_late = fields.Datetime(compute='_compute_scheduled_date_very_late', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ])

    @api.depends('scheduled_date', 'picking_type_id.days_very_late')
    def _compute_scheduled_date_very_late(self):
        for record in self:
            record.scheduled_date_very_late = record.scheduled_date + timedelta(days=record.picking_type_id.days_very_late)

class PickingType(models.Model):
    _inherit = "stock.picking.type"

    days_very_late = fields.Integer(help="Number of days to mark as very late", default=100)
    count_picking_to_process = fields.Integer(compute='_compute_count_picking_process_late')
    count_picking_very_late = fields.Integer(compute='_compute_count_picking_process_late')
    
    def _compute_count_picking_process_late(self):
        domains = {
                'count_picking_to_process': [('state','in',('assigned','confirmed'))],
                'count_picking_very_late':  [('scheduled_date_very_late', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)), ('state', 'in', ('assigned', 'waiting', 'confirmed'))]
            }
        for field_name, domain in domains.items():
            data = self.env['stock.picking']._read_group(
                domain +
                [('state', 'not in', ('done', 'cancel')), 
                ('picking_type_id', 'in', self.ids)],
                ['picking_type_id'], ['__count'])
            count = {picking_type.id: count for picking_type, count in data}
            for record in self:
                record[field_name] = count.get(record.id, 0)

    def get_action_picking_tree_to_process(self):
        return self._get_action('stock_picking_state_to_process.action_picking_tree_to_process')

    def get_action_picking_tree_very_late(self):
        return self._get_action('stock_picking_state_to_process.action_picking_tree_very_late')
    