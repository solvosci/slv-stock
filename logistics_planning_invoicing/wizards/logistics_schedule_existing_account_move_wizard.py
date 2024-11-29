# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class LogisticsScheduleExistingAccountMove(models.TransientModel):
    _name = 'logistics.schedule.existing.account.move.wizard'
    _description = "Logistics Schedule Add to Existing Invoice wizard"

    logistics_schedule_ids = fields.Many2many('logistics.schedule', 'logistics_schedule_existing_account_move_wizard_rel', readonly=True)
    carrier_id = fields.Many2one('res.partner', readonly=True)
    invoice_id = fields.Many2one('account.move', string="Invoice")
    invoice_line_id = fields.Many2one('account.move.line', string="Invoice Line")
    journal_id = fields.Many2one('account.journal', default=lambda self: self.env.user.company_id.logistics_schedule_default_journal_id)

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        self.invoice_line_id = False

    def add_invoice(self):
        self.invoice_line_id.agg_logistics_schedule_ids = [(4, x.id) for x in self.logistics_schedule_ids]
        self.logistics_schedule_ids.account_move_line_id = self.invoice_line_id
        self.logistics_schedule_ids.state = 'done'

        if len(self.logistics_schedule_ids) == 1:
            return self.logistics_schedule_ids.action_logistics_schedule_form_view()
