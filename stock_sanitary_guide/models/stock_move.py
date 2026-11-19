# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _prepare_capture_origin_vals(self, move_line, product_type, capture_date):
        vals = super()._prepare_capture_origin_vals(move_line, product_type, capture_date)
        guide = move_line.sanitary_guide_id
        vals["sanitary_guide_id"] = guide.id
        if guide.capture_date:
            vals["capture_date"] = guide.capture_date
        return vals
