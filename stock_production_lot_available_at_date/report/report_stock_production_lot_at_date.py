# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models, fields
from datetime import timedelta

class ReportStockProductionLotDate(models.TransientModel):
    _name = 'report.stock.production.lot.date'
    _description = 'Stock Production Lot Date Report'
    _order = 'lot_id'

    lot_id = fields.Many2one(comodel_name='stock.production.lot')
    product_id = fields.Many2one(comodel_name='product.product')
    qty = fields.Float(digits='Product Unit of Measure')
    uom_id = fields.Many2one(comodel_name='uom.uom', string='Unit of Measure')
    company_id = fields.Many2one(comodel_name='res.company')

    @api.model
    def _from_data_create(self, date, product_id):
        # TODO: The current filter is applied with "sm.date <= '{date} 00:00:00'", which evaluates the lots existence up to
        # the start of the day in UTC. This results in a 1-day offset when interpreted in local time (CEST).
        #
        # To mitigate this, we opted to increment the date by a whole day, so we query up to
        # the "start of the next day", which is effectively equivalent to querying "the end of the given day" in CEST.
        #
        # This is a partial solution: it doesn't properly account for time zones (UTC vs CEST).
        # We should calculate 00:00:00 CEST of the next day and convert it to UTC before applying it to the filter.
        date = date + timedelta(days=1)
        where_conditions = [
            "sm.state = 'done'",
            f"sm.date <= '{date.strftime('%Y-%m-%d %H:%M:%S')}'",
            "sml.lot_id IS NOT NULL",
            f"sml.company_id = {self.env.company.id}",
        ]

        if product_id:
            where_conditions.append(f"sml.product_id = {product_id.id}")

        where_clause = " AND ".join(where_conditions)

        sql_query = f"""
            SELECT
                row_number() OVER () AS id,
                sml.lot_id,
                pp.id as product_id,
                sml.product_uom_id,
                sml.company_id,
                SUM(
                    CASE
                        WHEN sl_src.usage IN ('customer', 'production', 'inventory') THEN sml.qty_done
                        ELSE 0
                    END
                ) -
                SUM(
                    CASE
                        WHEN sl_dest.usage IN ('customer', 'production', 'inventory') THEN sml.qty_done
                        ELSE 0
                    END
                ) AS net_qty
            FROM stock_move_line sml
            JOIN stock_move sm ON sm.id = sml.move_id
            JOIN stock_location sl_src ON sl_src.id = sml.location_id
            JOIN stock_location sl_dest ON sl_dest.id = sml.location_dest_id
            JOIN stock_production_lot pl ON pl.id = sml.lot_id
            JOIN product_product pp ON pp.id = sml.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE {where_clause}
            GROUP BY sml.lot_id, pp.id, sml.company_id, sml.product_uom_id
            HAVING ABS(
                SUM(
                    CASE
                        WHEN sl_src.usage IN ('customer', 'production', 'inventory') THEN sml.qty_done
                        ELSE 0
                    END
                ) -
                SUM(
                    CASE
                        WHEN sl_dest.usage IN ('customer', 'production', 'inventory') THEN sml.qty_done
                        ELSE 0
                    END
                )
            ) >= 0.001
        """

        self.env.cr.execute(sql_query)
        papds = self.browse()
        for row in self.env.cr.dictfetchall():
            papds |= self.create({
                "lot_id": row["lot_id"],
                "product_id": row["product_id"],
                "qty": row["net_qty"],
                "uom_id": row["product_uom_id"],
                "company_id": row["company_id"],
            })
        return papds
