# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class LogisticsSchedule(models.Model):
    _inherit = "logistics.schedule"

    sale_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        readonly=True,
        copy=False,
    )
    sale_order_id = fields.Many2one(
        related="sale_order_line_id.order_id",
        store=True,
    )

    def _prepare_ls_account_move_line(self, move_id):
        values = super()._prepare_ls_account_move_line(move_id)
        ls_id = self.browse(self.id.origin)
        if ls_id.sale_order_id and ls_id.sale_order_id.analytic_account_id:
            values.update({
                "analytic_account_id": ls_id.sale_order_id.analytic_account_id.id,
            })
        return values
