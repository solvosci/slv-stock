# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _apply_inventory(self):
        """
        Procedure:
        - (1) Obtain every stock inventory in progress involved in current quants
        - (2) Identify those quants that are not involved in stock inventories,
        -     or belong to a stock inventory but are actually marked as done
        -     => quants_not_in_invs => directly apply default behavior
        - (3) For those quants not in (2)-set, call _apply_inventory with the 
        -     inventory date they belong to 
        """
        inv_ids = self.env["stock.inventory"].search([
            ("stock_quant_ids", "in", self.ids),
            ("state", "=", "in_progress"),
        ])
        quants_not_in_invs = self - inv_ids.stock_quant_ids.filtered(
            lambda x: x.to_do
        )
        for inv in inv_ids:
            quants = (
                inv.stock_quant_ids.filtered(lambda x: x.to_do) - quants_not_in_invs
            ).with_context(
                stock_move_custom_date=inv.date
            )
            super(StockQuant, quants)._apply_inventory()
        super(StockQuant, quants_not_in_invs)._apply_inventory()
