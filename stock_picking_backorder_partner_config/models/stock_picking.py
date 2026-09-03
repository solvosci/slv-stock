# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models
from odoo.tools.float_utils import float_is_zero, float_compare

class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _pre_action_done_hook(self):
        if not self.env.context.get('skip_partner', False):
            for picking in self:
                create_partial_picking = picking.get_create_partial_picking()

                if create_partial_picking in ('by_default', 'ask'):
                    return super(StockPicking, picking)._pre_action_done_hook()
                else:
                    skip_backorder = picking.with_context(skip_backorder=True)
                    return super(StockPicking, skip_backorder)._pre_action_done_hook()
        return True

    def _check_backorder(self):
        prec = self.env["decimal.precision"].precision_get("Product Unit of Measure")
        backorder_pickings = super()._check_backorder()
        for picking in self:
            create_partial_picking = picking.get_create_partial_picking()
            if create_partial_picking != 'ask':
                continue
            if any(
                    (move.product_uom_qty and not move.picked) or
                    float_compare(move._get_picked_quantity(), move.product_uom_qty, precision_digits=prec) < 0
                    for move in picking.move_ids
                    if move.state != 'cancel'
            ):
                backorder_pickings |= picking
        return backorder_pickings

    def button_validate(self):
        if len(self) > 1:
            return super().button_validate()

        create_partial_picking = self.get_create_partial_picking()

        if create_partial_picking == 'by_default':
            return super().button_validate()

        self = self.filtered(lambda p: p.state != 'done')
        draft_picking = self.filtered(lambda p: p.state == 'draft')
        draft_picking.action_confirm()
        for move in draft_picking.move_ids:
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) and\
               not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                move.quantity = move.product_uom_qty

        # Sanity checks.
        if not self.env.context.get('skip_sanity_check', False):
            self._sanity_check()
        self.message_subscribe([self.env.user.partner_id.id])

        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        pickings_not_to_backorder = self.filtered(lambda p: create_partial_picking == 'never')
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder |= self.browse(self.env.context['picking_ids_not_to_backorder']).filtered(
                lambda p: create_partial_picking != 'always'
            )
        pickings_to_backorder = self - pickings_not_to_backorder
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()

        return True

    def get_create_partial_picking(self):
        create_partial_picking = self.partner_id.create_partial_delivery
        if self.picking_type_code == 'incoming':
            create_partial_picking = self.partner_id.create_partial_reception
        return create_partial_picking
