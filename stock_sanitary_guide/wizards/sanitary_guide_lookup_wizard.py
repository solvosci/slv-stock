# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SanitaryGuideLookupWizard(models.TransientModel):
    _name = "sanitary.guide.lookup.wizard"
    _description = "Sanitary Guide Lookup"

    move_line_id = fields.Many2one("stock.move.line", required=True)
    guide_number = fields.Char(required=True)
    new_zone_history_warning = fields.Boolean()

    @api.onchange("guide_number")
    def _onchange_guide_number(self):
        self.new_zone_history_warning = False
        if not self.guide_number:
            return
        guide = self.env["sanitary.guide"]._get_or_fetch(self.guide_number)
        self.new_zone_history_warning = self._zone_needs_new_history(guide)

    def action_confirm(self):
        self.ensure_one()
        guide = self.env["sanitary.guide"]._get_or_fetch(self.guide_number)
        self.move_line_id.sanitary_guide_id = guide.id
        if guide.capture_zone_id:
            self.move_line_id.capture_zone_id = guide.capture_zone_id.id
        if guide.biological_zone_id:
            self.move_line_id.biological_zone_id = guide.biological_zone_id.id
        return self.move_line_id.move_id.action_show_details()

    def _zone_needs_new_history(self, guide):
        self.ensure_one()
        types = self.move_line_id.product_intecmar_categ_ids
        if not types:
            return False
        for product_type in types:
            if guide.capture_zone_id and not self._zone_history_exists(
                "intecmar.capture.zone.status.history",
                [
                    ("capture_zone_id", "=", guide.capture_zone_id.id),
                    ("product_type_id", "=", product_type.id),
                    ("date_to", "=", False),
                ],
            ):
                return True
            if guide.biological_zone_id and not self._zone_history_exists(
                "intecmar.biological.zone.line",
                [
                    ("biological_zone_id", "=", guide.biological_zone_id.id),
                    ("capture_zone_id", "=", guide.capture_zone_id.id),
                    ("product_type_id", "=", product_type.id),
                ],
            ):
                return True
        return False

    def _zone_history_exists(self, model_name, domain):
        return bool(self.env[model_name].search_count(domain))
