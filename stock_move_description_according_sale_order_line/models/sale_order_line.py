# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def write(self, values):
        ret = super().write(values)
        if "name" in values:
            for move in self.filtered(lambda x: x.move_ids).move_ids:
                if move.picking_id.state not in ["done", "cancel"]:
                    move._set_description_picking()
        return ret
