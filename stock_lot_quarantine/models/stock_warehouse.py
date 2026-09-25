# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    quarantine_location_id = fields.Many2one(
        "stock.location",
        string="Quarantine Location (Purification)",
        domain="[('usage', '=', 'internal')]",
        check_company=True,
        help="Root of the quarantine subtree for this warehouse. Must "
            "be excluded from delivery routes.",
    )
