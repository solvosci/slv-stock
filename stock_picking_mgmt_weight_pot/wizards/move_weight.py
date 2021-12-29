# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class MoveWeight(models.TransientModel):
    _inherit = "stock.move.weight.wizard"

    def purchase_order_new(self):
        order_new = super().purchase_order_new()
        # By default, a programmaticaly created purchase will have already
        # order type filled with the first occurrence, or the partner one.
        # This process will override it, if needed
        if self.picking_id.picking_type_id.classification_pot_id:
            order_new.order_type = (
                self.picking_id.picking_type_id.classification_pot_id
            )
            order_new.onchange_order_type()
        return order_new
