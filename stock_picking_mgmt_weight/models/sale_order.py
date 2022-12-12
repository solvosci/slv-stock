# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, fields, models
from odoo.exceptions import Warning


class SaleOrder(models.Model):
    _inherit = "sale.order"

    has_pending_qty = fields.Boolean(
        compute="_compute_has_pending_qty",
        help="Instrumental field indicating if there's any pending quantity"
        " for this order",
    )
    shipping_resource_id = fields.Many2one(
        comodel_name="shipping.resource",
        default=lambda self: self.env["shipping.resource"].get_default(),
    )

    def _compute_has_pending_qty(self):
        for record in self:
            record.has_pending_qty = any([
                line.has_pending_qty for line in record.order_line
            ])

    def action_cancel_pending(self, custom_line=False):
        """
        Finishes selected order, cancelling pending quantities, or for a
        certain line.
        """
        # An error is not raised due to batch action with several orders launch
        # In that case, if orders with no pending quantities are selected, this
        #  process is simply ignored
        if not self.has_pending_qty:
            return

        pending_lines = (
            custom_line or
            self.order_line.filtered(lambda x: x.has_pending_qty)
        )
        pending_lines.move_ids.filtered(
            lambda x: x.state not in ["done", "cancel"]
        )._action_cancel()
        # TODO lock pickings fully cancelled

    def action_cancel_pending_multi(self):
        for record in self.browse(self.env.context["active_ids"]):
            record.action_cancel_pending()

    def action_confirm(self):
        """
        Cancel & pending quantities are sensible to former cancelled stock
        moves.
        When a SO is confirmed a stock move cleanup is made in order
        to prevent e.g. previous cancelled moves when SO was cancelled and
        moved to draft before this confirm action.        
        """
        if not self.env.context.get("skip_confirm_cancel_moves", False):
            cancelled_moves = self.order_line._unlink_cancelled_moves(
                unlink=False
            )
            if cancelled_moves:
                wiz = self.env["sale.order.confirm.wizard"].create({
                    "order_id": self.id,
                })
                return {
                    "type": "ir.actions.act_window",
                    "name": _("Warning"),
                    "res_model": "sale.order.confirm.wizard",
                    "view_type": "form",
                    "view_mode": "form",
                    "res_id": wiz.id,
                    "target": "new",
                }
            else:
                return super().action_confirm()
        else:
            self.order_line._unlink_cancelled_moves()
            return super().action_confirm()
