# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class StockPicking(models.Model):
    _inherit = ["stock.picking", "product.secondary.unit.mixin"]
    _name = "stock.picking"

    def _action_done(self):
        res = super()._action_done()

        for picking in self.filtered(lambda x: x.backorder_ids):
            picking.backorder_ids.move_ids._compute_secondary_uom_qty()
        return res
