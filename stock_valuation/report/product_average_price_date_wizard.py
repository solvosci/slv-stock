# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, models, fields


class ProductAveragePriceDateWizard(models.TransientModel):
    _name = "product.average.price.date.wizard"
    _description = "Product Average Price Date Wizard"

    date = fields.Date(default=fields.Date.context_today, required=True)
    warehouse_ids = fields.Many2many(
        comodel_name="stock.warehouse",
        string="Selected warehouses",
        help="Leave empty if every warehouse is required",
    )
    # TODO product categories?

    def get_average_prices(self):
        papds = self.env["product.average.price.date"]._from_data_create(
            self.date, self.warehouse_ids
        )

        return {
            "name": _("Product Average Prices at %s" % str(self.date)),
            "res_model": "product.average.price.date",
            "view_mode": "tree",
            "target": "current",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", papds.ids)],
            "context": {
                "search_default_filter_stock_non_zero": True,
                "search_default_groupby_product": (
                    len(self.warehouse_ids) != 1
                ),
            }
        }
