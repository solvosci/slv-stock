# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        touches_quarantine = False
        redirected_lots = self.env["stock.lot"]
        for move in self:
            for line in move.move_line_ids.filtered(
                lambda l: l.lot_id and l.quantity > 0
            ):
                lot = line.lot_id
                if lot.toxin_block_state != "blocked":
                    continue
                dest_in_quarantine = self._location_in_quarantine(
                    line.location_dest_id
                )
                if (
                    dest_in_quarantine
                    or move.picking_type_id.purification_allows_blocked_transit
                ):
                    touches_quarantine = touches_quarantine or dest_in_quarantine
                    continue
                mirror = (
                    line.location_dest_id._get_or_create_quarantine_mirror()
                    if line.location_dest_id.usage == "internal"
                    else None
                )
                if not mirror:
                    raise UserError(_(
                        "Lot %(lot)s is blocked due to a capture zone "
                        "closure (toxins) and cannot leave the "
                        "quarantine area until manually released.",
                        lot=lot.display_name,
                    ))
                line.location_dest_id = mirror.id
                touches_quarantine = True
                redirected_lots |= lot

        res = super(
            StockMove,
            self.with_context(quarantine_entry_authorized=True)
            if touches_quarantine else self,
        )._action_done(cancel_backorder=cancel_backorder)
        incoming_moves = self.filtered(
            lambda m: m.picking_type_id.code == "incoming" and m.product_id.intecmar_categ
        )
        if incoming_moves:
            incoming_moves._process_incoming_toxin_zone_control()
        if redirected_lots:
            redirected_lots._compute_single_location()
            redirected_lots.flush_recordset(["location_id"])
        return res

    def _process_incoming_toxin_zone_control(self):
        new_origin_vals = []
        blocked_lots = self.env["stock.lot"]

        for move in self:
            capture_date = move.date.date() if move.date else fields.Date.today()
            for move_line in move.move_line_ids:
                if not move_line.lot_id:
                    continue
                if not move_line.capture_zone_id:
                    move.picking_id.message_post(
                        body="Product subject to capture zone control was "
                        "received without a capture zone selected on the line. "
                        "Toxin control was NOT applied to lot %s."
                        % move_line.lot_id.name
                    )
                    continue

                new_origin_vals += [
                    self._prepare_capture_origin_vals(
                        move_line, product_type, capture_date
                    )
                    for product_type in move_line.product_id.intecmar_categ
                ]
                blocked_lots |= move_line.lot_id

        if new_origin_vals:
            self.env["lot.capture.zone.origin"].sudo().create(new_origin_vals)
        blocked_lots._evaluate_toxin_block()

    def _prepare_capture_origin_vals(self, move_line, product_type, capture_date):
        return {
            "lot_id": move_line.lot_id.id,
            "capture_zone_id": move_line.capture_zone_id.id,
            "product_type_id": product_type.id,
            "capture_date": capture_date,
        }
