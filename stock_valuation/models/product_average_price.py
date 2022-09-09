# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models, api, _


class ProductAveragePrice(models.Model):
    _name = "product.average.price"
    _description = "Product Average Price by Warehouse"

    history_average_price_ids = fields.One2many('product.history.average.price', 'product_average_price_id')
    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('stock.warehouse')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True, required=True)
    average_price = fields.Monetary(compute="_compute_average_price", store=True)

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

    @api.depends("history_average_price_ids.average_price")
    def _compute_average_price(self):
        for record in self:
            record.average_price = record.history_average_price_ids.sorted(key=lambda r: r.date, reverse=True)[0].average_price
