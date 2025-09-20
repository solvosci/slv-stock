# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)

def pre_migrate(cr, registry):
    # TODO MIG
    # Starting from v17, there's a new non-stored field called warehouse_id,
    #  so we need to move and preserve this former value
    # NOT TESTED YET
    if not column_exists(cr, "stock_valuation_layer", "phap_warehouse_id"):
        create_column(cr, "stock_valuation_layer", "phap_warehouse_id", "integer")
        _logger.info("Adding phap_warehouse_id column values to stock_valuation_layer...")
        cr.execute(
            """
            update
                stock_valuation_layer
            set
                phap_warehouse_id=phap.warehouse_id
            from
                stock_valuation_layer svl
            inner join
                product_history_average_price phap
                on phap.id=svl.history_average_price_id
            where
                svl.id=stock_valuation_layer.id
            ;
            """
        )
                    