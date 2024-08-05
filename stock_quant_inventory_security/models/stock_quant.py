# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _is_inventory_mode(self):
        return (
            super()._is_inventory_mode()
            and self.user_has_groups(
                "stock_quant_inventory_security.group_stock_quant_inventory_edit"
            )
        )
