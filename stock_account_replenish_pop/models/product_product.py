# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _svl_replenish_stock(self, description, products_orig_quantity_svl):
        refill_stock_svl_list = super()._svl_replenish_stock(
            description, products_orig_quantity_svl
        )
        for svl_vals in refill_stock_svl_list:
            svl_vals["description"] += svl_vals.pop("rounding_adjustment", "")
        return refill_stock_svl_list
