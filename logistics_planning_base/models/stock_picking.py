# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    logistics_schedule_ids = fields.One2many(
        'logistics.schedule',
        'picking_id',
        copy=False,
    )
    logistics_schedule_count = fields.Integer(compute='_compute_logistics_schedule_count')

    def _compute_logistics_schedule_count(self):
        for record in self:
            record.logistics_schedule_count = len(record.logistics_schedule_ids)

    def _get_prepared_ls_returns(self):
        # To be inherited
        # Returns prepared logistics schedule values list and a boolean
        #  indicating if generated schedules should be automatically moved to ready
        self.ensure_one()
        return [], False
