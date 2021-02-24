# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, api, models


class StockPickingMixin(models.AbstractModel):
    _name = "stock.picking.state.mixin"
    _description = "Stock Picking Mixin"
    
    picking_status = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('assigned', 'Ready'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], compute='_compute_picking_status', readonly=True, store=True)

    @api.depends('picking_ids.state')
    def _compute_picking_status(self):
        for order in self:
            pickings = order.picking_ids.filtered(
                lambda p: p.state != "cancel"
            )
            if pickings:
                order.picking_status = pickings.sorted(
                    key="scheduled_date"
                )[-1].state
            else:
                order.picking_status = False
