# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _action_cancel_pending_create(self):
        order_new = super()._action_cancel_pending_create()
        # TODO make it safely (what happens if 0 or 2 types is returned?)
        order_new.order_type = self.classification_order_ids.order_type
        order_new.onchange_order_type()
        return order_new
