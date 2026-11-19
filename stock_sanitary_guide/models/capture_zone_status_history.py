# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class CaptureZoneStatusHistory(models.Model):
    _inherit = "intecmar.capture.zone.status.history"

    source = fields.Selection(
        selection_add=[("guide", "Sanitary Guide")],
        ondelete={"guide": "set default"},
        help="'guide' marks an entry with no real INTECMAR tracking "
            "behind it (bootstrapped from the Xunta zone catalog, or "
            "resolved/updated from a sanitary guide)",
    )
