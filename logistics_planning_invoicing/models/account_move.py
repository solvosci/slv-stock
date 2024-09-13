# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    # TODO rename this field, as strictly reflects "initially linked logistic
    #      schedules", only used during invoice creation
    logistics_schedule_ids = fields.Many2many(
        'logistics.schedule',
        'account_move_id',
        copy=False,
    )
    logistics_schedule_count = fields.Integer(compute='_compute_logistics_schedule_count')

    @api.onchange('logistics_schedule_ids')
    def _onchange_logistics_schedule_auto_complete(self):
        self.fiscal_position_id = self.partner_id.property_account_position_id
        new_lines = self.env['account.move.line']
        aml_dict_list = self.logistics_schedule_ids._prepare_ls_account_move_lines(self)
        for aml_dict in aml_dict_list:
            new_line = new_lines.new(aml_dict)
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
            record.logistics_schedule_count = sum(
                len(aml._get_all_logistics_schedule_ids())
                for aml in record.invoice_line_ids
            )

    def button_cancel(self):
        # TODO prevent user with warning?
        self._ls_secure_unlink()
        super().button_cancel()

    def unlink(self):
        # TODO prevent user with warning?
        self._ls_secure_unlink()
        return super().unlink()

    def _ls_secure_unlink(self):
        self.invoice_line_ids._ls_secure_unlink()
