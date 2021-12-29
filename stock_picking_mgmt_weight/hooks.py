# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging
from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    logging.getLogger('odoo.addons.stock_picking_mgmt_weight').info(
        'Adding pending locations, sequences and pìcking types to '
        'current warehouses')

    env = api.Environment(cr, SUPERUSER_ID, {})
    for warehouse in env["stock.warehouse"].search([]):
        new_vals = warehouse._create_or_update_sequences_and_picking_types()
        warehouse.write(new_vals)
