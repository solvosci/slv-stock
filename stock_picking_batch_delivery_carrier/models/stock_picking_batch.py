# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier'
        )

    @api.depends('carrier_id')
    def _compute_allowed_picking_ids(self):
        super()._compute_allowed_picking_ids()
        for batch in self.filtered(lambda b: b.carrier_id):
                batch.allowed_picking_ids = batch.allowed_picking_ids.filtered(
                    lambda picking: picking.carrier_id == batch.carrier_id
                )

    def write(self, vals):
        res = super().write(vals)
        if vals.get('carrier_id'):
            self._sanity_check()
        return res

    @api.depends('carrier_id.name')
    @api.depends_context('show_carrier_in_batch_display')
    def _compute_display_name(self):
        if not self.env.context.get('show_carrier_in_batch_display',False):
            return super()._compute_display_name()
        for rec in self:
            if rec.carrier_id:
                rec.display_name = f"{rec.carrier_id.name} - {rec.name}"
            else:
                rec.display_name = (_("No carrier - %s") % rec.name)
