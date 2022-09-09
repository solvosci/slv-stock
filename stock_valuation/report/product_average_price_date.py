# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, models, fields


class ProductAveragePriceDate(models.TransientModel):
    _name = "product.average.price.date"
    _description = "Product Average Price at Date"
    _order = "product_id, warehouse_id"

    date = fields.Date(readonly=True)
    company_id = fields.Many2one("res.company", readonly=True)
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        readonly=True,
    )
    product_id = fields.Many2one("product.product", readonly=True)
    warehouse_id = fields.Many2one("stock.warehouse", readonly=True)
    average_price = fields.Monetary(readonly=True)
    stock_quantity = fields.Float(readonly=True)
    stock_valuation = fields.Monetary(readonly=True)

    @api.model
    def _from_data_create(self, date, warehouse_ids=False):
        """
        Populates report with PHAPs selected
        TODO read_group in order to prevent SQL usage?
        """
        sql_query = """
            select
                phap.*
            from (
                select
                    max(date) maxdate
                    , product_id
                    , warehouse_id
                    , company_id
                from
                    product_history_average_price
                where
                    date <= '%s'
                    and company_id = %s
                    %s
                group by
                    product_id, warehouse_id, company_id
            ) V
            inner join
                product_history_average_price phap on
                    phap.date=V.maxdate and
                    phap.product_id=V.product_id and
                    phap.warehouse_id=V.warehouse_id and
                    phap.company_id=V.company_id
        """
        extra_condition = ""
        if warehouse_ids:
            extra_condition = (
                "and warehouse_id in (%s)"
                % str(warehouse_ids.ids)[1:-1]
            )
        self.env.cr.execute(
            sql_query
            % (str(date), self.env.company.id, extra_condition)
        )
        papds = self.browse()
        for row in self.env.cr.dictfetchall():
            papds |= self.create({
                "date": date,
                "company_id": row["company_id"],
                "product_id": row["product_id"],
                "warehouse_id": row["warehouse_id"],
                "average_price": row["average_price"],
                "stock_quantity": row["stock_quantity"],
                "stock_valuation": row["stock_valuation"],
            })
        return papds
