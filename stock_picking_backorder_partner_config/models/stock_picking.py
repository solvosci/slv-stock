# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models
from odoo.tools.float_utils import float_compare, float_is_zero


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _pre_action_done_hook(self):
        if not self.env.context.get('skip_partner', False):
            for picking in self:
                create_partial_picking = picking.get_create_partial_picking()
                if create_partial_picking in ('by_default', 'ask'):
                    res = super(StockPicking, picking)._pre_action_done_hook()
                else:
                    skip_backorder = picking.with_context(skip_backorder=True)
                    res = super(StockPicking, skip_backorder)._pre_action_done_hook()
                if res is not True:
                    return res
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
        if len(self) == 1 and self.get_create_partial_picking() == 'by_default':
            return super().button_validate()

        has_custom_policy = any(p.get_create_partial_picking() in ('never', 'always') for p in self)
        if not has_custom_policy and len(self) > 1:
            return super().button_validate()

        standard_pickings = self.filtered(lambda p: p.get_create_partial_picking() in ('by_default', 'ask'))
        if standard_pickings:
            res = super(StockPicking, standard_pickings).button_validate()
            if res is not True:
                return res

        custom_pickings = self - standard_pickings
        if not custom_pickings:
            return True

        valid_pickings = custom_pickings.filtered(lambda p: p.state != 'done')
        draft_picking = valid_pickings.filtered(lambda p: p.state == 'draft')
        draft_picking.action_confirm()
        for move in draft_picking.move_ids:
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding) and \
            not float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                move.quantity = move.product_uom_qty

        if not self.env.context.get('skip_sanity_check', False):
            valid_pickings._sanity_check()
        valid_pickings.message_subscribe([self.env.user.partner_id.id])

        ctx = self.env.context.copy()
        if not ctx.get('button_validate_picking_ids'):
            ctx['button_validate_picking_ids'] = self.ids
        res = super(StockPicking, valid_pickings.with_context(**ctx))._pre_action_done_hook()
        if res is not True:
            return res

        pickings_not_to_backorder = valid_pickings.filtered(lambda p: p.get_create_partial_picking() == 'never')
        if ctx.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder |= self.browse(ctx['picking_ids_not_to_backorder']).filtered(
                lambda p: p.get_create_partial_picking() != 'always'
            )
        pickings_to_backorder = valid_pickings - pickings_not_to_backorder

        if pickings_to_backorder:
            pickings_to_backorder.with_context(cancel_backorder=False)._action_done()
        if pickings_not_to_backorder:
            pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()

        return True

    def get_create_partial_picking(self):
        self.ensure_one()
        create_partial_picking = self.partner_id.create_partial_delivery
        if self.picking_type_code == 'incoming':
            create_partial_picking = self.partner_id.create_partial_reception
        return create_partial_picking
