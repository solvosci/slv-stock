# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ReturnPickingLS(models.TransientModel):
    _name = "stock.return.picking.ls.wizard"
    _description = "Picking return wizard - LS confirmation"

    stock_return_picking_id = fields.Many2one(
        comodel_name="stock.return.picking",
        required=True,
        readonly=True,
    )

    def create_return_ls_ok(self):
        return self.stock_return_picking_id.with_context(
            skip_ask_return=True, create_ls=True
        ).create_returns()

    def create_return_ls_ko(self):
        return self.stock_return_picking_id.with_context(
            skip_ask_return=True, create_ls=False
        ).create_returns()
