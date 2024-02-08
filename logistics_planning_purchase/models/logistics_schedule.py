# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class LogisticsSchedule(models.Model):
    _inherit = "logistics.schedule"

    purchase_order_line_id = fields.Many2one(
        comodel_name="purchase.order.line",
        readonly=True,
        copy=False,
    )
    purchase_order_id = fields.Many2one(
        related="purchase_order_line_id.order_id",
        store=True,
    )

    def _prepare_ls_account_move_line(self, move_id):
        values = super()._prepare_ls_account_move_line(move_id)
        ls_id = self.browse(self.id.origin)
        if ls_id.purchase_order_line_id and ls_id.purchase_order_line_id.account_analytic_id:
            values.update({
                "analytic_account_id": ls_id.purchase_order_line_id.account_analytic_id.id,
            })
        return values

    @api.onchange("stock_move_id")
    def _onchange_stock_move_id(self):
        super()._onchange_stock_move_id()
        if (
            self.schedule_finished
            and self.purchase_order_line_id.order_id.incoterm_id.ls_invoice_disabled
        ):
            self.is_finished = True

    # def write(self, values):
    #     to_finished = self.browse()
    #     unfinished = self
    #     ret = False
    #     if "schedule_finished" in values and values["schedule_finished"]:
    #         to_finished |= self.filtered(
    #             lambda x: x.purchase_order_line_id.order_id.incoterm_id.ls_invoice_disabled
    #         )
    #         unfinished -= to_finished
    #         values_to_finished = {
    #             "is_finished": True,
    #             **values,
    #         }
    #         ret = super(LogisticsSchedule, to_finished).write(values_to_finished)
    #     ret |= super(LogisticsSchedule, unfinished).write(values)
    #     return ret
