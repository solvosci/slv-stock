# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    if not openupgrade.column_exists(
        env.cr, "stock_move", "rel_sale_order_id"
    ):
        openupgrade.logged_query(
            env.cr,
            """ALTER TABLE stock_move
            ADD COLUMN rel_sale_order_id int;
            COMMENT ON COLUMN stock_move.rel_sale_order_id IS 'Related Sale Order';
            """,
        )
        openupgrade.logged_query(
            env.cr,
            """
            UPDATE
                stock_move
            SET
                rel_sale_order_id=sol.order_id
            FROM
                stock_move sm
            INNER JOIN
                sale_order_line sol on sol.id=sm.sale_line_id
            WHERE
                stock_move.id=sm.id
            """,
        )
