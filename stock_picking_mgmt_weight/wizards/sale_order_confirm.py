# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class SaleOrderConfirmWizard(models.TransientModel):
    _name = "sale.order.confirm.wizard"
    _description = "Sale Order Confirm Wizard"

    order_id = fields.Many2one("sale.order", readonly=True)

    def action_confirm(self):
        self.ensure_one()
        self.order_id.with_context(
            skip_confirm_cancel_moves=True
        ).action_confirm()
