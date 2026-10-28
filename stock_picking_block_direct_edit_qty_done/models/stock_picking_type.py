# © 2026 Solvos Consultoría Informática (http://www.solvos.es)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    block_direct_edit_qty_done = fields.Boolean(
        string="Block direct edit of done quantity",
        compute="_compute_block_direct_edit_qty_done",
        store=True,
        readonly=False,
    )

    @api.depends("code")
    def _compute_block_direct_edit_qty_done(self):
        for record in self:
            record.block_direct_edit_qty_done = record.code == "outgoing"
