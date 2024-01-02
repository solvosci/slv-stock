# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    logistics_schedule_ids = fields.Many2many(
        'logistics.schedule',
        'account_move_id',
        copy=False,
    )
    logistics_schedule_count = fields.Integer(compute='_compute_logistics_schedule_count')

    @api.onchange('logistics_schedule_ids')
    def _onchange_logistics_schedule_auto_complete(self):
        # TODO invoice origin
        self.fiscal_position_id = self.partner_id.property_account_position_id
        new_lines = self.env['account.move.line']
        for logistic_schedule in self.logistics_schedule_ids:
            new_line = new_lines.new(logistic_schedule._prepare_ls_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            taxes = new_line._get_computed_taxes()
            if taxes and self.fiscal_position_id:
                taxes = self.fiscal_position_id.map_tax(taxes, partner=self.partner_id)
            new_line.tax_ids = taxes            
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        self._onchange_currency()
        self.invoice_partner_bank_id = self.bank_partner_id.bank_ids and self.bank_partner_id.bank_ids[0]

    def _compute_logistics_schedule_count(self):
        for record in self:
            record.logistics_schedule_count = len(record.logistics_schedule_ids)

    def button_cancel(self):
        # TODO prevent user with warning?
        self._ls_secure_unlink()
        super().button_cancel()

    def unlink(self):
        # TODO prevent user with warning?
        self._ls_secure_unlink()
        return super().unlink()

    def _ls_secure_unlink(self):
        aml_ids = self.invoice_line_ids.sudo().filtered(
            lambda x: x.logistics_schedule_id
        )
        if aml_ids:
            ls_ids = aml_ids.logistics_schedule_id
            aml_ids.write({"logistics_schedule_id": False})
            # TODO implement done->ready action method?
            ls_ids.write({"state": "ready"})
