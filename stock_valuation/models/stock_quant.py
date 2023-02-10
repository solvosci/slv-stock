# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    average_price = fields.Monetary(
        string="Price",
        compute="_compute_value",
        groups="stock.group_stock_manager",
    )

    def _compute_value(self):
        """
        For those products with the special flag of standard price
        with warehouse and daily price value is overriden
        """
        super()._compute_value()

        average_quants = self.filtered(
            lambda x: x.product_id.warehouse_valuation
        )
        if average_quants:
            # Different average prices of interest caching
            PAP = self.env["product.average.price"].sudo()
            average_prices = PAP.search(
                [("product_id", "in", average_quants.mapped("product_id").ids)]
            )
            average_price_products = average_prices.mapped("product_id")
            dict_ap = {p.id: {} for p in average_price_products}
            for app in average_prices:
                dict_ap[app.product_id.id][app.warehouse_id.id] = app.average_price

            # TODO check speed process (warehouse detection is poor implemented)
            for quant in average_quants:
                warehouse = quant.location_id.get_warehouse()
                quant.average_price = (
                    dict_ap.get(quant.product_id.id, False)
                    and dict_ap[quant.product_id.id].get(warehouse.id, 0.0)
                    or 0.0
                )
                quant.value = quant.quantity * quant.average_price
        for other_quant in (self - average_quants):
            other_quant.average_price = other_quant.product_id.standard_price
