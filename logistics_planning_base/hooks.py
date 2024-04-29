# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

import logging


def post_init_hook(cr, registry):
    logging.getLogger('odoo.addons.logistics_planning_base').info(
        'Updating stock.move with logistics_schedule_disabled field to True')

    cr.execute(
        """
        UPDATE stock_move
        SET logistics_schedule_disabled = True
        WHERE state = 'done'
        """
    )
