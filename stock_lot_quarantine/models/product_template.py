# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    purifiable = fields.Boolean(
        string="Purifiable",
        help="Indicates whether this product may require purification "
            "(quarantine) before it can be sold.",
    )
    purification_hours = fields.Float(
        string="Purification Hours",
        default=12.0,
        help="Minimum time (in hours) that a lot of this product must "
            "remain in quarantine when received NOT purified.",
    )
