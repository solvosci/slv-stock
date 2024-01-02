# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    logistics_schedule_id = fields.Many2one('logistics.schedule')

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        lines_w_ls = lines.filtered(lambda x: x.logistics_schedule_id) 
        for line in lines_w_ls:
            line.logistics_schedule_id.account_move_line_id = line.id
        lines_w_ls.logistics_schedule_id._action_done()
        return lines

    def write(self, values):
        if "logistics_schedule_id" in values:
            logistics_schedule_id = (
                values.get("logistics_schedule_id")
                and self.env["logistics.schedule"].browse(values.get("logistics_schedule_id"))
                or False
            )
            if logistics_schedule_id:
                logistics_schedule_id.account_move_line_id = self
            else:
                self.logistics_schedule_id.account_move_line_id = False
        return super().write(values)
