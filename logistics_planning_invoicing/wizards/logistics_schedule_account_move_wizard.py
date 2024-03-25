# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, _


class LogisticsScheduleAccountMove(models.TransientModel):
    _name = 'logistics.schedule.account.move.wizard'
    _description = "Logistics Schedule Create Invoice wizard"

    logistics_schedule_ids = fields.Many2many('logistics.schedule', readonly=True)
    company_id = fields.Many2one('res.company', related='logistics_schedule_ids.company_id')
    carrier_id = fields.Many2one('res.partner', readonly=True)
    journal_id = fields.Many2one('account.journal', default=lambda self: self.env.user.company_id.logistics_schedule_default_journal_id.id)
    ref = fields.Char(string="Bill Reference")

    def create_invoice(self):
        action = self.env.ref('account.action_move_in_invoice_type')
        result = action.read()[0]
        result['context'] = self.logistics_schedule_ids._prepare_ls_account_move()
        result['context'].update({
            "default_partner_id": self.carrier_id.id,
            "default_journal_id": self.journal_id.id,
            "default_company_id": self.company_id.id,
            "default_ref": self.ref,
        })
        res = self.env.ref('account.view_move_form', False)
        form_view = [(res and res.id or False, 'form')]
        result['views'] = form_view

        # TODO why this line?
        result['context']['logistics_schedule_ids'] = self.logistics_schedule_ids.ids

        return result
