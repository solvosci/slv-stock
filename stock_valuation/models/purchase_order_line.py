# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def write(self, values):
        """
        When price of a line has changed before a purchase line is done,
        SVLs should be changed and linked PHAPs recomputed & SVLs updated
        """
        res = super().write(values)
        if values.get("price_unit"):
            line_moves = self.env["stock.move"]
            affected_moves = self.env["stock.move"]
            for line in self.filtered(
                lambda x: x.state in ["purchase", "done"]
                and x.product_id.warehouse_valuation
                and x.move_ids
            ):
                line_moves = line.move_ids
                svls = line_moves.sudo().stock_valuation_layer_ids
                if svls:
                    affected_moves |= line_moves
                    for svl in svls:
                        svl.unit_cost = values.get("price_unit")
                        svl.value = svl.unit_cost * svl.quantity
            # Moves price unit update for internal coherence and future
            #  returns, or even if move is not done yet, because SVLs will
            #  take the value from it
            if line_moves:
                line_moves.write({"price_unit": values.get("price_unit")})
            if affected_moves:
                affected_moves._compute_phaps_and_update_slvs()

        return res
