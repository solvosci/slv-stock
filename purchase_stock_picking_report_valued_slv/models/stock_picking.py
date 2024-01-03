# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    purchase_currency_id = fields.Many2one(
        related="purchase_id.currency_id",
        readonly=True,
        string="Currency",
        related_sudo=True
    )
    purchase_amount_untaxed = fields.Monetary(
        currency_field="purchase_currency_id",
        compute="_compute_purchase_amount_all",
        compute_sudo=True
    )
    purchase_amount_total = fields.Monetary(
        currency_field="purchase_currency_id",
        compute="_compute_purchase_amount_all",
        compute_sudo=True
    )

    def _compute_purchase_amount_all(self):

        for pick in self:
            purchase_amount_untaxed = sum(
                line.purchase_price_subtotal for line in pick.move_line_ids
            )
            purchase_amount_total = 0
            for line in pick.move_line_ids:
                purchase_amount_total += (
                    line.purchase_price_subtotal - (line.purchase_price_subtotal * (line.purchase_line.discount / 100))
                )
            pick.update(
                {
                    "purchase_amount_untaxed": purchase_amount_untaxed,
                    "purchase_amount_total": purchase_amount_total,
                }
            )
