# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
import logging
from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)

def pre_init_hook(cr):
    new_cols = [
        ("account_move_line", "val_operation", "varchar"),
        ("account_move_line", "val_operation_origin", "varchar"),
    ]
    for data in new_cols:
        if not column_exists(cr, data[0], data[1]):
            _logger.info(f"Creating column '{data[1]}' in {data[0]}")
            create_column(cr, data[0], data[1], data[2])

    cr.execute("""
        UPDATE account_move_line aml
        SET
            val_operation = CASE
                WHEN sm.scrapped IS TRUE THEN 'scrap'
                WHEN src.usage = 'inventory' OR dst.usage = 'inventory'
                    THEN 'inv_adjust'
                WHEN sm.origin_returned_move_id IS NOT NULL THEN
                    CASE
                        WHEN dst.usage = 'internal' THEN 'out_return'
                        ELSE 'in_return'
                    END
                WHEN dst.usage = 'internal' AND src.usage != 'internal'
                    THEN 'incoming'
                WHEN src.usage = 'internal' AND dst.usage != 'internal'
                    THEN 'outgoing'
                ELSE NULL
            END,
            val_operation_origin = COALESCE(sp.name, sm.reference, sm.origin)
        FROM account_move am
        JOIN stock_move sm ON am.stock_move_id = sm.id
        JOIN stock_location src ON sm.location_id = src.id
        JOIN stock_location dst ON sm.location_dest_id = dst.id
        LEFT JOIN stock_picking sp ON sm.picking_id = sp.id
        WHERE aml.move_id = am.id;
    """)
    # Special case - price update (has no stock move linked for the account move)
    cr.execute("""
        UPDATE
            account_move_line
        SET
            val_operation = 'price_update'
            , val_operation_origin = pp.default_code
        FROM
            account_move_line aml
        INNER JOIN
            account_move am
            ON aml.move_id=am.id
        INNER JOIN
            stock_valuation_layer svl
            ON svl.account_move_id = am.id
        INNER JOIN
            product_product pp
            ON pp.id = aml.product_id
        WHERE
            account_move_line.id = aml.id
            AND am.stock_move_id IS NULL
    """)
    _logger.info("Account Move Line Valuation Operation: UPDATE executed successfully.")
