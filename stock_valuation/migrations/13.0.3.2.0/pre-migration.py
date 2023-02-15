# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "stock_valuation_layer", "origin_type"
    ):
        openupgrade.logged_query(
            env.cr,
            """ALTER TABLE stock_valuation_layer
            ADD COLUMN origin_type character varying
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE
                stock_valuation_layer
            SET
                origin_type=case
                    when sm.purchase_line_id is not null then 'purchase'
                    when sm.sale_line_id is not null then 'sale'
                    when sm.scrapped is true then 'scrap'
                    when spt.code = 'internal' then 'internal'
                    when slo.usage = 'inventory' or sld.usage = 'inventory' then 'adjustment'
                    else ''
                end
            FROM
                stock_valuation_layer svl
            INNER JOIN
                stock_move sm on sm.id=svl.stock_move_id
            INNER JOIN
                stock_location slo on slo.id=sm.location_id
            INNER JOIN
                stock_location sld on sld.id=sm.location_dest_id
            LEFT JOIN
                stock_picking sp on sp.id=sm.picking_id
            LEFT JOIN
                stock_picking_type spt on spt.id=sp.picking_type_id
            WHERE
                stock_valuation_layer.id = svl.id
            """,
        )
