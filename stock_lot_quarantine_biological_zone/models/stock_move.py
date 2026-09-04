# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_capture_origin_vals(self, move_line, product_type, capture_date):
        vals = super()._prepare_capture_origin_vals(
            move_line, product_type, capture_date
        )
        vals["biological_zone_id"] = move_line.biological_zone_id.id
        return vals
