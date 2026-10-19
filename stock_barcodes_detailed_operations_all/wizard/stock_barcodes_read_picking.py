# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    @api.depends("picking_id.move_line_ids")
    def _compute_move_line_ids(self):
        self.move_line_ids = self.picking_id.move_line_ids.sorted(
            key=lambda sml: (sml.write_date, sml.create_date), reverse=True
        )

    def _prepare_move_line_values(self, candidate_move, available_qty):
        vals = super()._prepare_move_line_values(candidate_move, available_qty)
        vals["quantity"] = available_qty
        vals["picked"] = bool(available_qty)
        return vals
