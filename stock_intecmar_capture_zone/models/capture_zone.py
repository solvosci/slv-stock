# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ShellfishCaptureZone(models.Model):
    _name = "intecmar.capture.zone"
    _description = "Capture Zone (INTECMAR)"
    _order = "code"

    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Capture Zone code as published by INTECMAR.",
    )
    name = fields.Char(
        string="Name",
        required=True,
        help="Capture Zone name as published by INTECMAR.",
    )
    status_ids = fields.One2many(
        "intecmar.capture.zone.status.history", "capture_zone_id",
        string="Administrative Status History",
    )

    _code_unique = models.Constraint(
        "unique(code)",
        "This capture zone code is already registered.",
    )

    @api.depends("name", "code")
    def _compute_display_name(self):
        for zone in self:
            zone.display_name = "%s (%s)" % (zone.name, zone.code)
