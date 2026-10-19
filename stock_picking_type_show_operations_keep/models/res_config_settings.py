# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    def set_values(self):
        StockPickingType = self.env['stock.picking.type'].with_context(
            active_test=False
        )
        picking_types_so = StockPickingType.search([
            ("code", "!=", "incoming"),
            ("show_operations", "=", False)
        ]).ids
        res = super().set_values()
        pt_so_new = StockPickingType.browse(picking_types_so).filtered(
            lambda x: x.show_operations
        )
        if pt_so_new:
            pt_so_new.write({"show_operations": False})
        return res
