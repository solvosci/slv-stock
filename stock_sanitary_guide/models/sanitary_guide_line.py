# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SanitaryGuideLine(models.Model):
    _name = "sanitary.guide.line"
    _description = "Sanitary Guide Capture Line"

    guide_id = fields.Many2one(
        "sanitary.guide",
        string="Sanitary Guide",
        required=True,
        ondelete="cascade",
        index=True,
    )
    fao_code = fields.Char(string="FAO Code", help="FAO species code, e.g. OYG.")
    common_name = fields.Char(string="Common Name")
    scientific_name = fields.Char(string="Scientific Name")
    quantity_kg = fields.Float(string="Quantity (kg)", digits=(16, 2))
