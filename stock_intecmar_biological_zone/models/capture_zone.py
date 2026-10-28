# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShellfishCaptureZone(models.Model):
    _inherit = "intecmar.capture.zone"

    biological_zone_line_ids = fields.One2many(
        "intecmar.biological.zone.line", "capture_zone_id",
        string="Biological Classifications",
    )
