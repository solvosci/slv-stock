# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models

class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def _get_action(self, action_xmlid):
        action = super()._get_action(action_xmlid)
        if self:
            action["context"]["show_deliver_to"] = (self.code == "outgoing")
        return action
