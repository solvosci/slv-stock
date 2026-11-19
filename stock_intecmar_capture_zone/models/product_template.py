# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    intecmar_categ = fields.Many2many(
        "intecmar.capture.product.type",
        string="INTECMAR Product Types",
        help="INTECMAR product/cultivation categories this product "
            "belongs to.",
    )
