# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShellfishBiologicalZone(models.Model):
    _name = "intecmar.biological.zone"
    _description = "Biological Zone (Xunta de Galicia)"
    _rec_name = "code"

    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Classification zone code as published by Intecmar.",
    )
    name = fields.Char(
        string="Name",
        required=True,
        help="Classification zone name as published by Intecmar.",
    )
    line_ids = fields.One2many(
        "intecmar.biological.zone.line", "biological_zone_id",
        string="Lines",
    )

    _code_unique = models.Constraint(
        "unique(code)",
        "This classification zone code is already registered.",
    )
