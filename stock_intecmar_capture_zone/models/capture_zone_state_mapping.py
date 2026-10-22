# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShellfishCaptureZoneStateMapping(models.Model):
    _name = "intecmar.capture.zone.state.mapping"
    _description = "INTECMAR State Wording Mapping"
    _rec_name = "external_label"

    external_label = fields.Char(
        string="Status Name",
        required=True,
        help="State name exactly as published by INTECMAR (e.g. "
             "'Aberta'), or a custom name for manually-created states.",
    )
    blocks_extraction = fields.Boolean(
        string="Blocks Extraction",
        default=True,
        help="Whether this state means the capture zone/type is closed to "
             "extraction. New states start blocking until reviewed.",
    )

    _external_label_unique = models.Constraint(
        "unique(external_label)",
        "This INTECMAR wording is already mapped.",
    )
