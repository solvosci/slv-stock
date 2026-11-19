# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    received_purified = fields.Boolean(
        string="Received Already Purified?",
        default=False,
        help="Check if this lot/line arrives ALREADY purified from "
            "origin.",
    )
    product_purifiable = fields.Boolean(
        related="product_id.purifiable", store=False
    )
