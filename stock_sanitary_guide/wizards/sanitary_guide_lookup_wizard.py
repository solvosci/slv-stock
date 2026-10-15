# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class SanitaryGuideLookupWizard(models.TransientModel):
    _name = "sanitary.guide.lookup.wizard"
    _description = "Sanitary Guide Lookup"

    move_line_id = fields.Many2one("stock.move.line", required=True)
    guide_number = fields.Char(required=True)

    def action_confirm(self):
        self.ensure_one()
        guide = self.env["sanitary.guide"]._get_or_fetch(self.guide_number)
        self.move_line_id.sanitary_guide_id = guide.id
        if guide.capture_zone_id:
            self.move_line_id.capture_zone_id = guide.capture_zone_id.id
        if guide.biological_zone_id:
            self.move_line_id.biological_zone_id = guide.biological_zone_id.id
        return self.move_line_id.move_id.action_show_details()
