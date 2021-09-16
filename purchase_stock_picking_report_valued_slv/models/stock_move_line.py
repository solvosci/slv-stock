# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    purchase_line = fields.Many2one(
        related="move_id.purchase_line_id",
        readonly=True,
        string="Related order line"
    )
    purchase_currency_id = fields.Many2one(
        related="purchase_line.currency_id",
        readonly=True,
        string="Purchase Currency"
    )
    purchase_tax_id = fields.Many2many(
        related="purchase_line.taxes_id",
        readonly=True,
        string="Purchase Tax"
    )
    purchase_price_unit = fields.Float(
        related="purchase_line.price_unit",
        readonly=True,
        string="Purchase price unit"
    )
    purchase_discount = fields.Float(
        related="purchase_line.discount",
        readonly=True,
        string="Purchase discount (%)"
    )
    purchase_price_subtotal = fields.Monetary(
        currency_field="purchase_currency_id",
        compute="_compute_purchase_order_line_fields",
        string="Price subtotal",
        compute_sudo=True
    )

    def _compute_purchase_order_line_fields(self):
        for line in self:
            purchase_line = line.purchase_line
            price_unit = (
                purchase_line.price_subtotal / purchase_line.product_uom_qty
                if purchase_line.product_uom_qty
                else purchase_line._get_discounted_price_unit()
            )
            taxes = line.purchase_tax_id.compute_all(
                price_unit=price_unit,
                currency=line.purchase_currency_id,
                quantity=line.qty_done or line.product_qty,
                product=line.product_id,
                partner=purchase_line.order_id.dest_address_id,
            )

            line.update(
                {
                    "purchase_price_subtotal": taxes["total_excluded"],
                }
            )
