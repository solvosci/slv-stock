# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShellfishBiologicalZoneLine(models.Model):
    _name = "intecmar.biological.zone.line"
    _description = "Biological Zone Line (Xunta de Galicia)"

    biological_zone_id = fields.Many2one(
        "intecmar.biological.zone",
        string="Classification Zone",
        required=True,
        ondelete="cascade",
        index=True,
    )
    capture_zone_id = fields.Many2one(
        "intecmar.capture.zone",
        string="Capture Zone",
        required=True,
        index=True,
    )
    product_type_id = fields.Many2one(
        "intecmar.capture.product.type",
        string="Product Type",
        required=True,
        index=True,
    )
    state = fields.Char(
        string="Classification",
        help="Sanitary classification (e.g. 'A', 'B', 'C') as returned "
             "by the Intecmar API",
    )
