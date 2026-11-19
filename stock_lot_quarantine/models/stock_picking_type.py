# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    purification_allows_blocked_transit = fields.Boolean(
        string="Allows Blocked Lots (Purification)",
        help="If checked, this operation type may move a blocked "
            "(in-quarantine) lot outside the quarantine area, e.g. "
            "Manufacturing. Leave unchecked on Delivery Orders unless "
            "you intend blocked lots to reach customers.",
    )
