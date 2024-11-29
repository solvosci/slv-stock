# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    logistics_schedule_id = fields.Many2one('logistics.schedule', copy=False)
    agg_logistics_schedule_ids = fields.Many2many(
        comodel_name="logistics.schedule",
        copy=False,
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

    def unlink(self):
        # TODO prevent user with warning?
        self._ls_secure_unlink()
        return super().unlink()

    def _ls_secure_unlink(self):
        ls_ids = self.sudo()._get_all_logistics_schedule_ids()
        if ls_ids:
            ls_ids.account_move_line_id.write({
                "logistics_schedule_id": False,
                "agg_logistics_schedule_ids": False,
            })
            ls_ids.write({
                "account_move_line_id": False,
                "state": "ready",
            })

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        context = self.env.context
        if context.get('logistics_planning_invoicing_existing', False):
            domain = args or []
            domain += [("name", operator, name)]
            return self.search(domain).name_get()

        return super().name_search(name=name, args=args, operator=operator, limit=limit)

    def name_get(self):
        res = []
        context = self.env.context
        if context.get('logistics_planning_invoicing_existing', False):
            for record in self:
                name = f"[{record.product_id.name}] {record.move_id.name}({record.name}) - {record.price_unit} {record.company_currency_id.symbol} ({record.quantity} {record.product_uom_id.name})"
                res.append((record.id, name))
            return res
        return super().name_get()
