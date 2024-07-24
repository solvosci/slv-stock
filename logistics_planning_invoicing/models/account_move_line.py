# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    logistics_schedule_id = fields.Many2one('logistics.schedule')
    agg_logistics_schedule_ids = fields.Many2many(
        comodel_name="logistics.schedule",
        string="Aggregated logistics schedules",
    )

    def _get_all_logistics_schedule_ids(self):
        return (
            self.logistics_schedule_id
            | self.agg_logistics_schedule_ids
        )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            all_ls_ids = line._get_all_logistics_schedule_ids().sudo()
            if all_ls_ids:
                all_ls_ids.write({
                    "account_move_line_id": line.id,
                })
                all_ls_ids._action_done()
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
