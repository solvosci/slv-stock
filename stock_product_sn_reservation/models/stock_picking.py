# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, models


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "sn.locked.mixin"]

    @api.depends("state", "picking_type_id.code")
    def _compute_sn_locked_invisible(self):
        super()._compute_sn_locked_invisible()
        locked_inv_pick_ids = self.filtered(
            lambda x: x.state != "assigned" or x.picking_type_id.code != "outgoing"
        )
        locked_inv_pick_ids.update({"sn_locked_invisible": True})
        (self - locked_inv_pick_ids).update({"sn_locked_invisible": False})
