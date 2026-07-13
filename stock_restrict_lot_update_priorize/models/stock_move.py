# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    restict_lot_priorized = fields.Boolean(
        string="Force lot reservation",
        compute="_compute_restict_lot_priorized",
        store=True,
        readonly=False,
        copy=False,        
        default=False,
        help=
        """
        When restict lot is filled and this check selected,
        the lot will be reserved even if there are existing reservations,
        stealing them, if needed and possible
        """,
    )

    @api.depends("restrict_lot_id")
    def _compute_restict_lot_priorized(self):
        self.filtered(lambda x: not x.restrict_lot_id).write({
            "restict_lot_priorized": False
        })


    def _action_assign(self):
        super()._action_assign()
        candidate_moves_unreserve = self.browse([])
        candidate_moves_reassign = self.browse([])
        for move in self.filtered(
            lambda x: (
                x.restrict_lot_id
                and x.restict_lot_priorized
                and x.product_uom_qty > x.reserved_availability
            )
        ):
            # Moves that have restrict lot priorized and are not fully reserved
            # We need to find another suitable move to steal the reservation
            # If we found it, we'll unassign them and try to assign this move again
            quant_ids = move.restrict_lot_id.quant_ids.filtered(
                lambda x: x.location_id in move.location_id.child_internal_location_ids
            )
            if sum(quant_ids.mapped("reserved_quantity")) > move.reserved_availability:
                # We'll only try to steal reservations from other moves that have
                #  no the same restrict lot filled
                candidate_moves_lines = self.env["stock.move.line"].search(
                    [
                        ("move_id", "!=", move.id),
                        ("lot_id", "=", move.restrict_lot_id.id),
                        ("state", "in", ["partially_available", "assigned"]),
                    ],
                    order="product_uom_qty desc",
                ).filtered(lambda x: x.move_id.restrict_lot_id != move.restrict_lot_id)
                if candidate_moves_lines:
                    pending_qty = move.product_uom_qty - move.reserved_availability
                    for mls in candidate_moves_lines:
                        candidate_moves_unreserve |= mls.move_id
                        pending_qty -= mls.product_uom_qty
                        if pending_qty <= 0:
                            break
                    candidate_moves_reassign |= move
 
        if candidate_moves_unreserve:
            # TODO this will unassign even reservation for other lots (e.g. a
            # move has two lots reserved)
            # Not tested, but it could be replaced by simply delete
            # stock.move.line with exact lot record
            candidate_moves_unreserve._do_unreserve()

        if candidate_moves_reassign:
            candidate_moves_reassign._action_assign()
            # We try assign again the previously unassigned moves, if they can
            # be filled by another lots
            candidate_moves_unreserve._action_assign()
