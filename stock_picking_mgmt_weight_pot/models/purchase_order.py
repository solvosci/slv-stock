# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _action_cancel_pending_create(self):
        order_new = super()._action_cancel_pending_create()
        # TODO test "0" order types corner case
        order_new.order_type = (
            self.classification_order_ids
            and self.classification_order_ids[0].order_type
            or False
        )
        order_new.onchange_order_type()
        return order_new
