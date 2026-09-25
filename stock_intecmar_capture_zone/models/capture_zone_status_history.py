# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class CaptureZoneStatusHistory(models.Model):
    _name = "intecmar.capture.zone.status.history"
    _description = "Capture Zone Administrative Status (history)"
    _order = "date_from desc"

    capture_zone_id = fields.Many2one(
        "intecmar.capture.zone",
        string="Capture Zone",
        required=True,
        ondelete="cascade",
    )
    product_type_id = fields.Many2one(
        "intecmar.capture.product.type",
        string="Product Type",
        required=True,
        ondelete="restrict",
    )
    state_id = fields.Many2one(
        "intecmar.capture.zone.state.mapping",
        string="Status",
        required=True,
        help="The INTECMAR state in force for this period. Whether it "
             "blocks extraction is configured on the state itself.",
    )
    blocks_extraction = fields.Boolean(
        related="state_id.blocks_extraction",
        store=True,
        readonly=True,
        help="Technical: mirrors the linked state's blocking flag, for "
             "fast filtering. Not editable here -- change it on the "
             "state itself.",
    )
    date_from = fields.Date(string="In force from", required=True)
    date_to = fields.Date(
        string="In force until",
        help="Leave empty if this period is still active.",
    )
    report_type = fields.Selection(
        [
            ("intecmar_bulletin", "INTECMAR Bulletin"),
            ("resolution", "Administrative Resolution"),
            ("lab_analysis", "Lab Analysis"),
            ("manual", "Manual Entry"),
            ("other", "Other"),
        ],
        string="Source Document Type",
        default="manual",
        required=True,
    )
    report_reference = fields.Char(
        string="Reference",
        help="Bulletin/resolution number or identifier.",
    )
    attachment_ids = fields.Many2many(
        "ir.attachment", string="Supporting Documents"
    )
    notes = fields.Text()
    source = fields.Selection(
        [("manual", "Manual"), ("automatic", "Automatic (scraper)")],
        default="manual",
        required=True,
        help="Whether this record was entered manually or by the "
             "INTECMAR sync.",
    )

    @api.depends("date_from", "date_to", "report_type")
    def _compute_display_name(self):
        report_type_labels = dict(self._fields["report_type"]._description_selection(self.env))
        for status in self:
            status.display_name = "%s → %s — %s" % (
                status.date_from, status.date_to or "Now",
                report_type_labels.get(status.report_type, status.report_type),
            )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._sweep_affected_lots()
        return records

    def _sweep_affected_lots(self):
        affected_lots = self.env["stock.lot"]
        for status in self:
            domain = [
                ("capture_zone_id", "=", status.capture_zone_id.id),
                ("product_type_id", "=", status.product_type_id.id),
                ("capture_date", ">=", status.date_from),
            ]
            if status.date_to:
                domain.append(("capture_date", "<=", status.date_to))
            affected_lots |= self.env["lot.capture.zone.origin"].search(
                domain
            ).mapped("lot_id")
        affected_lots.filtered(
            lambda lot: lot.toxin_block_state != "released"
        )._evaluate_toxin_block()

    @api.constrains("capture_zone_id", "product_type_id", "date_from", "date_to")
    def _check_no_overlap(self):
        for rec in self:
            domain = [
                ("capture_zone_id", "=", rec.capture_zone_id.id),
                ("product_type_id", "=", rec.product_type_id.id),
                ("id", "!=", rec.id),
                "|", ("date_to", "=", False), ("date_to", ">=", rec.date_from),
            ]
            if rec.date_to:
                domain.append(("date_from", "<=", rec.date_to))
            other = self.search(domain, limit=1)
            if other:
                raise ValidationError(
                    "Overlapping status period for capture zone '%s' / "
                    "type '%s' (conflicts with period starting %s)."
                    % (rec.capture_zone_id.display_name, rec.product_type_id.code,
                        other.date_from)
                )
