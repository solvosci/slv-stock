# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, models
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        redirected_lots = self._check_purification_leak()
        res = super()._action_done(cancel_backorder=cancel_backorder)
        for move in self.filtered(
            lambda x: x.picking_type_id.code == "incoming" and x.product_id.purifiable
        ):
            move._process_incoming_purification()
        self._settle_blocked_lots_in_stock()
        if redirected_lots:
            redirected_lots._compute_single_location()
            redirected_lots.flush_recordset(["location_id"])
        return res

    def _check_purification_leak(self):
        redirected_lots = self.env["stock.lot"]
        for move in self:
            for line in move.move_line_ids.filtered(
                lambda l: l.lot_id and l.quantity > 0
            ):
                lot = line.lot_id
                dest_in_quarantine = self._location_in_quarantine(line.location_dest_id)
                if lot.purification_state == "blocked":
                    if (
                        dest_in_quarantine
                        or move.picking_type_id.purification_allows_blocked_transit
                    ):
                        continue
                    mirror = (
                        line.location_dest_id._get_or_create_quarantine_mirror()
                        if line.location_dest_id.usage == "internal"
                        else None
                    )
                    if not mirror:
                        raise UserError(_(
                            "Lot %(lot)s is still in quarantine and "
                            "cannot leave the quarantine area until "
                            "released.",
                            lot=lot.display_name,
                        ))
                    line.location_dest_id = mirror.id
                    redirected_lots |= lot
                elif dest_in_quarantine and not self.env.context.get(
                    "quarantine_entry_authorized"
                ):
                    raise UserError(_(
                        "Lot %(lot)s is not in quarantine and cannot "
                        "enter a quarantine location.",
                        lot=lot.display_name,
                    ))
        return redirected_lots

    @staticmethod
    def _location_in_quarantine(location):
        return location._is_within(location.warehouse_id.quarantine_location_id)

    def _process_incoming_purification(self):
        self.ensure_one()
        if not self.picking_type_id.warehouse_id.quarantine_location_id:
            self.picking_id.message_post(
                body=_(
                    "Purifiable product received but this warehouse "
                    "has no Quarantine Location configured."
                )
            )
            return
        for move_line in self.move_line_ids.filtered(lambda l: l.lot_id):
            if move_line.received_purified:
                move_line.lot_id._mark_exempt()
            else:
                move_line.lot_id._start_quarantine(self.product_id.purification_hours)
                self._redirect_chained_move_to_quarantine(move_line)

    def _redirect_chained_move_to_quarantine(self, move_line):
        chained_moves = self.move_dest_ids.filtered(
            lambda m: m.state not in ("done", "cancel")
        )
        if not chained_moves:
            return
        mirror = move_line.location_dest_id._get_or_create_quarantine_mirror()
        if not mirror:
            return
        chained_moves.location_dest_id = mirror.id
        chained_moves.move_line_ids.filtered(
            lambda l: l.lot_id == move_line.lot_id
        ).location_dest_id = mirror.id

    def _settle_blocked_lots_in_stock(self):
        for lot in self.mapped("move_line_ids").filtered(
            lambda l: l.lot_id
            and l.product_id.purifiable
            and l.lot_id.purification_state == "blocked"
        ).mapped("lot_id"):
            lot._send_stock_to_quarantine()
