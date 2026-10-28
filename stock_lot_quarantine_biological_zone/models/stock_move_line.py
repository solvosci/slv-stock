# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    biological_zone_id = fields.Many2one(
        "intecmar.biological.zone",
        string="Biological Zone",
        help="Microbiological classification zone this line was received "
            "from.",
    )
    valid_biological_zone_ids = fields.Many2many(
        "intecmar.biological.zone",
        compute="_compute_valid_biological_zone_ids",
        help="Technical field feeding biological_zone_id's domain.",
    )

    @api.depends("capture_zone_id", "product_intecmar_categ_ids")
    def _compute_valid_biological_zone_ids(self):
        candidates = self.env["intecmar.biological.zone.line"].search([
            ("capture_zone_id", "in", self.capture_zone_id.ids),
        ])
        candidates_by_zone = {}
        for candidate in candidates:
            candidates_by_zone.setdefault(
                candidate.capture_zone_id.id, []
            ).append(candidate)

        for line in self:
            valid = self.env["intecmar.biological.zone"]
            for candidate in candidates_by_zone.get(line.capture_zone_id.id, []):
                if candidate.product_type_id.id in line.product_intecmar_categ_ids.ids:
                    valid |= candidate.biological_zone_id
            line.valid_biological_zone_ids = valid
