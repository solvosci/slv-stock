# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models, fields, api, _


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    carrier_id = fields.Many2one(
        comodel_name='delivery.carrier'
        )
    require_same_carrier_in_batch = fields.Boolean(
        related="picking_type_id.require_same_carrier_in_batch",
    )
    picking_sender_ref = fields.Char(
        string="Sender Reference",
        help="Reference of the picking for the batch, if any.",
        compute="_compute_picking_sender_ref",
        store=True,
        readonly=False,
    )

    @api.depends('carrier_id', 'picking_type_id.require_same_carrier_in_batch', 'picking_ids.carrier_id')
    def _compute_allowed_picking_ids(self):
        super()._compute_allowed_picking_ids()
        for batch in self.filtered(
            lambda b: b.carrier_id
            and (not b.picking_type_id or b.picking_type_id.require_same_carrier_in_batch)
        ):
            batch.allowed_picking_ids = batch.allowed_picking_ids.filtered(
                lambda picking: picking.carrier_id == batch.carrier_id
            )

    @api.depends('picking_ids', 'picking_ids.carrier_tracking_ref', 'picking_type_code')
    def _compute_picking_sender_ref(self):
        for batch in self.filtered(lambda b: not b.picking_sender_ref and b.picking_type_code == 'incoming'):
            batch.picking_sender_ref = batch.picking_ids.filtered(lambda p: p.carrier_tracking_ref)[:1].carrier_tracking_ref

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
