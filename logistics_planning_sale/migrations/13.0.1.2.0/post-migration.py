# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from openupgradelib import openupgrade 


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE
            logistics_schedule
        SET
            partner_id=so.partner_shipping_id
        FROM
            logistics_schedule ls
        INNER JOIN
            sale_order so on so.id=ls.sale_order_id
        WHERE
            ls.id=logistics_schedule.id
            and ls.sale_order_line_id is not null
            and ls.stock_move_id is null
            and ls.state not in ('cancel', 'done')
            and ls.partner_id <> so.partner_shipping_id
        ;
        """,
    )
