# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo import api, SUPERUSER_ID
from odoo.tools.sql import column_exists, create_column

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    # COLUMNS CREATION IN ORDER TO PREVENT COMPUTE EXECUTION
    new_cols = [
        ("stock_picking", "warehouse_view_location_src_id", "integer"),
        ("stock_picking", "warehouse_view_location_dest_id", "integer"),
        ("stock_move", "warehouse_view_location_src_id", "integer"),
        ("stock_move", "warehouse_view_location_dest_id", "integer"),
    ]
    for data in new_cols:        
        if not column_exists(cr, data[0], data[1]):
            _logger.info(f"Creating column '{data[0]}' in {data[1]}")
            create_column(cr, data[0], data[1], data[2])


def post_init_hook(cr, registry):
    # Only for active moves and pickings initialization is important
    env = api.Environment(cr, SUPERUSER_ID, {})
    domain_active = [("state", "not in", ["done", "cancel"])]

    picking_ids = env["stock.picking"].search(domain_active)
    _logger.info("Updating {} active picking(s)...".format(len(picking_ids)))
    for pick in picking_ids:
        pick.warehouse_view_location_src_id = pick.location_id.warehouse_id.view_location_id
        pick.warehouse_view_location_dest_id = pick.location_dest_id.warehouse_id.view_location_id

    move_ids = env["stock.move"].search(domain_active)
    _logger.info("Updating {} active move(s)...".format(len(move_ids)))
    for move in move_ids:
        move.warehouse_view_location_src_id = move.location_id.warehouse_id.view_location_id
        move.warehouse_view_location_dest_id = move.location_dest_id.warehouse_id.view_location_id
