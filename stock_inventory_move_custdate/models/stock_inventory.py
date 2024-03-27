# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_state_to_in_progress(self):
        super().action_state_to_in_progress()
        self.stock_quant_ids.update({"current_inventory_id": self.id})

    def action_state_to_done(self):
        super().action_state_to_done()
        self.stock_quant_ids.update({"current_inventory_id": False})

    def action_state_to_draft(self):
        self.stock_quant_ids.update({"current_inventory_id": False})
        super().action_state_to_draft()

    def action_view_inventory_adjustment(self):
        result = super().action_view_inventory_adjustment()
        result["context"].update({
            "hide_quantity_at_date": False,
            # "default_to_do": True,
            # "default_current_inventory_id": self.id,
        })
        return result
