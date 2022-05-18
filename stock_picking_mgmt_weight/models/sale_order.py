# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


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

    def action_cancel_pending(self):
        """
        Finishes selected orders, cancelling pending quantities.
        Pending pickings are cancelled as result of this process, not vice versa
        """
        # An error is not raised due to batch action with several orders launch
        # In that case, if orders with no pending quantities are selected, this
        #  process is simply ignored
        if not self.has_pending_qty:
            return

        pending_lines = self.order_line.filtered(lambda x: x.has_pending_qty)
        for line in pending_lines:
            # TODO better get it from to-cancel pickings?
            line.qty_cancelled += line.pending_qty

        cancel_pickings = pending_lines.mapped(
            "move_ids.picking_id"
        ).filtered(lambda x: x.state not in ["done", "cancel"])
        cancel_pickings.action_cancel()

    def action_cancel_pending_multi(self):
        for record in self.browse(self.env.context["active_ids"]):
            record.action_cancel_pending()
