# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import timedelta

from odoo import api, fields, models


class LotCaptureZoneOrigin(models.Model):
    _inherit = "lot.capture.zone.origin"

    sanitary_guide_id = fields.Many2one(
        "sanitary.guide",
        string="Sanitary Guide",
        help="Sanitary guide (Documento de orixe) this capture came in with.",
    )
    needs_review = fields.Boolean(
        string="Needs Review",
        compute="_compute_needs_review",
        store=True,
        help="True when this origin's own zone(s) no longer match its "
            "sanitary guide's current data",
    )

    @api.depends(
        "capture_zone_id", "biological_zone_id", "sanitary_guide_id",
        "sanitary_guide_id.capture_zone_id", "sanitary_guide_id.biological_zone_id",
    )
    def _compute_needs_review(self):
        for origin in self:
            origin.needs_review = origin.sanitary_guide_id and (
                origin.capture_zone_id != origin.sanitary_guide_id.capture_zone_id
                or origin.biological_zone_id != origin.sanitary_guide_id.biological_zone_id
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records.filtered("sanitary_guide_id"):
            record._apply_capture_zone_guide_status()
            record._apply_biological_zone_guide_line()
        return records

    def _apply_capture_zone_guide_status(self):
        self.ensure_one()

        effective_date = self.sanitary_guide_id.capture_date or fields.Date.today()
        open_entry = self.env["intecmar.capture.zone.status.history"].search([
            ("capture_zone_id", "=", self.capture_zone_id.id),
            ("product_type_id", "=", self.product_type_id.id),
            ("date_to", "=", False),
        ], limit=1)
        if open_entry and open_entry.source != "guide":
            return

        if self.sanitary_guide_id.biotoxin_zone_status:
            label = self.sanitary_guide_id.biotoxin_zone_status.strip()
            state = self.env["intecmar.capture.zone.state.mapping"].search([("external_label", "=ilike", label)], limit=1)
            if not state:
                state = self.env["intecmar.capture.zone.state.mapping"].create({"external_label": label})
        else:
            state = self.env.ref("stock_sanitary_guide.capture_zone_state_undetermined")

        if open_entry and open_entry.state_id == state:
            return

        if open_entry:
            open_entry.date_to = effective_date - timedelta(days=1)
        self.env["intecmar.capture.zone.status.history"].create({
            "capture_zone_id": self.capture_zone_id.id,
            "product_type_id": self.product_type_id.id,
            "state_id": state.id,
            "date_from": effective_date,
            "report_type": "other",
            "report_reference": self.sanitary_guide_id.guide_number,
            "source": "guide",
        })

    def _apply_biological_zone_guide_line(self):
        self.ensure_one()
        if not (
            self.biological_zone_id
            and self.capture_zone_id
            and self.product_type_id
            and self.sanitary_guide_id.sanitary_qualification
        ):
            return

        exists = self.env["intecmar.biological.zone.line"].search_count([
            ("biological_zone_id", "=", self.biological_zone_id.id),
            ("capture_zone_id", "=", self.capture_zone_id.id),
            ("product_type_id", "=", self.product_type_id.id),
        ])
        if exists:
            return
        self.env["intecmar.biological.zone.line"].create({
            "biological_zone_id": self.biological_zone_id.id,
            "capture_zone_id": self.capture_zone_id.id,
            "product_type_id": self.product_type_id.id,
            "state": self.sanitary_guide_id.sanitary_qualification,
        })
        self._compute_sanitary_state()
