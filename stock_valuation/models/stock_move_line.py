# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from math import copysign

from odoo import _, models
from odoo.exceptions import ValidationError


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def write(self, values):
        """
        After a move line is done, when an internal transfer/purchase/sale
        changes its quantity a subsequent PHAP y SVL update is needed.
        For other moves, this change is forbidden
        """
        if not self:
            return super().write(values)

        update_svls = self.env["stock.valuation.layer"]
        moves = self.env["stock.move"]
        val_keys = values.keys()
        if "qty_done" in val_keys and "state" not in val_keys:
            mls = self.filtered(
                lambda x: x.product_id.warehouse_valuation
                and (
                    x.picking_code == "internal"
                    or x.move_id.purchase_line_id
                    or x.move_id.sale_line_id
                )
                and x.state == "done"
            )
            moves = mls.mapped("move_id")

            # We'll only update transfer SVLs moves, because "delta" purchase
            #  and sale SVLs will be generated during write() move method
            # TODO unify procedure creating also "delta" internal transfer
            #      pair SVLs instead of updating existing ones
            update_svls = moves.filtered(
                lambda x: x.picking_code == "internal"
            ).sudo().stock_valuation_layer_ids

            other_mls = self - mls
            if other_mls.filtered(
                lambda x: x.product_id.warehouse_valuation
                and x.state == "done"
            ):
                raise ValidationError(_(
                    "For those products with standard warehouse valuation,"
                    " only purchase, sale & internal transfers quantities are "
                    "allowed to be changed when a move is done"
                ))

        # Preserving original SVL (move) date is mandatory for every new
        #   created SVL, so we need to pass it
        # Not every move update operation needs this data, but there's no
        #  problem passing it anyway (as we know)
        for ml in self:
            ml = ml.with_context(stock_move_custom_date=ml.date)
            res = super(StockMoveLine, ml).write(values)
            # For SVL, stock_move_action_done_custdate_val only covers
            #  recently new marked-as-done moves, soy we need to manually
            #  update the date
            # TODO directly cover it in stock_move_action_done_custdate_val
            #      addon
            ml.move_id.sudo().stock_valuation_layer_ids.create_date_update(
                ml.date
            )

        # TODO when transfers update are covered with "delta" SVLs this code
        #      should be removed
        if update_svls:
            for svl in update_svls:
                svl.quantity = copysign(
                    svl.stock_move_id.quantity_done,
                    svl.quantity
                )
                svl.value = svl.quantity * svl.unit_cost

        if moves:
            moves._compute_phaps_and_update_slvs()

        return res
