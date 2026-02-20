# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class WizCandidatePicking(models.TransientModel):
    _inherit = "wiz.candidate.picking"

    origin = fields.Char(
        related="picking_id.origin",
    )
