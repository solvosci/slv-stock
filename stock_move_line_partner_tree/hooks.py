# © 2022 Solvos Consultoría Informática (<https://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    """Speed up the installation of the module on an existing Odoo instance"""
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name='stock_move_line' AND
        column_name='picking_partner_id'
    """
    )
    if not cr.fetchone():
        _logger.info("Creating field picking_partner_id on stock_move_line")
        cr.execute(
            """
            ALTER TABLE stock_move_line
                ADD COLUMN picking_partner_id integer,
                ADD CONSTRAINT stock_move_line_picking_partner_id_fkey
                    FOREIGN KEY (picking_partner_id)
                    REFERENCES res_partner (id) MATCH SIMPLE
                    ON UPDATE NO ACTION
                    ON DELETE SET NULL;
        """
        )
        _logger.info("Filling picking_partner_id on stock_move_line")
        cr.execute(
            """
            UPDATE stock_move_line
            SET picking_partner_id = sp.partner_id
            FROM stock_move_line sml
            LEFT JOIN stock_picking sp on sp.id = sml.picking_id
            WHERE stock_move_line.id = sml.id
        """
        )
