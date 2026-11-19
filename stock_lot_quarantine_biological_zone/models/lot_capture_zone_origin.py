# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class LotCaptureZoneOrigin(models.Model):
    _inherit = "lot.capture.zone.origin"

    biological_zone_id = fields.Many2one(
        "intecmar.biological.zone",
        string="Biological Zone",
    )
    sanitary_state = fields.Char(
        string="Sanitary Classification",
        compute="_compute_sanitary_state",
        store=True,
        help="Sanitary classification (e.g. 'A', 'B', 'C') for this exact "
            "biological zone, capture zone and product type.",
    )

    @api.depends("biological_zone_id", "capture_zone_id", "product_type_id")
    def _compute_sanitary_state(self):
        if not self:
            return
        lines = self.env["intecmar.biological.zone.line"].search([
            ("biological_zone_id", "in", self.biological_zone_id.ids),
            ("capture_zone_id", "in", self.capture_zone_id.ids),
            ("product_type_id", "in", self.product_type_id.ids),
        ])
        by_key = {
            (line.biological_zone_id.id, line.capture_zone_id.id, line.product_type_id.id): line
            for line in lines
        }
        for origin in self:
            line = by_key.get(
                (origin.biological_zone_id.id, origin.capture_zone_id.id, origin.product_type_id.id)
            )
            origin.sanitary_state = line.state if line else False
