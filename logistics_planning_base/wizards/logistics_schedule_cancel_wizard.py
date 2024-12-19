# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class LogisticsScheduleCancel(models.TransientModel):
    _name = 'logistics.schedule.cancel.wizard'
    _description = "Logistics Schedule Cancel wizard"

    logistics_schedule_ids = fields.Many2many('logistics.schedule', readonly=True)

    def button_cancel(self):
        self.logistics_schedule_ids._action_cancel()
