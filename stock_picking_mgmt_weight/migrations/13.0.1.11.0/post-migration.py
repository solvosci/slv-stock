from openupgradelib import openupgrade  # pylint: disable=W7936


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET pending_qty = 0.0
        WHERE pending_qty < 0.0""",
    )
