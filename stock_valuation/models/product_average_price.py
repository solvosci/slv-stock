# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models, api, _
from odoo.tools.float_utils import float_compare


class ProductAveragePrice(models.Model):
    _name = "product.average.price"
    _description = "Product Average Price by Warehouse"

    history_average_price_ids = fields.One2many('product.history.average.price', 'product_average_price_id')
    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('stock.warehouse')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True, required=True)
    average_price = fields.Monetary(
        compute="_compute_average_price_stock",
        store=True,
    )
    stock_quantity = fields.Float(
        compute="_compute_average_price_stock",
        digits="Product Unit of Measure",
        store=True,
    )
    stock_zero = fields.Integer(
        compute="_compute_average_price_stock",
        store=True,
        help="""
            float_compare based stock condition value:
            - 1 if is positive
            - 0 if is zero
            - -1 if is negative
        """,
    )

    def name_get(self):
        # TODO display_name instead of name_get()?
        return [
            (
                pap.id,
                _("%s in %s")
                %
                (pap.product_id.display_name, pap.warehouse_id.name),
            )
            for pap in self
        ]

    @api.depends(
        "history_average_price_ids.average_price",
        "history_average_price_ids.stock_quantity",
    )
    def _compute_average_price_stock(self):
        for record in self:
            last_phap = record.history_average_price_ids.sorted(
                key=lambda r: r.date, reverse=True
            )[0]
            record.write({
                "average_price": last_phap.average_price,
                "stock_quantity": last_phap.stock_quantity,
                "stock_zero": float_compare(
                    last_phap.stock_quantity,
                    0.0,
                    precision_rounding=record.product_id.uom_id.rounding or 0.001
                ),
            })
