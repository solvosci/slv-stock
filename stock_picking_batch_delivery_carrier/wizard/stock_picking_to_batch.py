# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, _
from odoo.exceptions import UserError


class StockPickingToBatch(models.TransientModel):
    _inherit = 'stock.picking.to.batch'

    def attach_pickings(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids'))
        checked_pickings = pickings.filtered(
            lambda p: p.picking_type_id.require_same_carrier_in_batch
        )
        if any(not p.carrier_id for p in checked_pickings):
            raise UserError(_("All pickings must have a carrier assigned. At least one does not."))

        carriers = checked_pickings.mapped('carrier_id')
        if len(carriers) > 1:
            raise UserError(_("All selected pickings must have the same carrier."))
        if self.mode != 'new' and carriers and self.batch_id.carrier_id != carriers:
            raise UserError(_("The carrier of the batch must match the carrier of the pickings."))
        ctx = self.env.context.copy()
        ctx.update(
            {
                "default_carrier_id": carriers.id if len(carriers) == 1 else False,
            }
        )
        return super(StockPickingToBatch, self.with_context(ctx)).attach_pickings()
