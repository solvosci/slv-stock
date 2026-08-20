# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class LotCaptureZoneOrigin(models.Model):
    _name = "lot.capture.zone.origin"
    _description = "Lot Capture Origin (capture zone + type + date)"

    lot_id = fields.Many2one(
        "stock.lot", required=True, ondelete="cascade", index=True,
    )
    company_id = fields.Many2one(
        related="lot_id.company_id", store=True, readonly=True, index=True,
    )
    capture_zone_id = fields.Many2one(
        "intecmar.capture.zone", string="Capture Zone", required=True,
    )
    product_type_id = fields.Many2one(
        "intecmar.capture.product.type", string="Product Type",
        required=True,
    )
    capture_date = fields.Date(required=True)
    status_id = fields.Many2one(
        "intecmar.capture.zone.status.history",
        string="Applicable Status Record",
        compute="_compute_status_id",
        store=True,
        help="Status period in force for this capture zone, type and date.",
    )
    status_blocks_extraction = fields.Boolean(
        related="status_id.blocks_extraction", string="Blocks Extraction",
        readonly=True,
    )
    status_external_label = fields.Char(
        related="status_id.state_id.external_label", string="INTECMAR Status",
        readonly=True,
    )

    @api.depends("capture_zone_id", "product_type_id", "capture_date")
    def _compute_status_id(self):
        if not self:
            return
        candidates = self.env["intecmar.capture.zone.status.history"].search(
            [
                ("capture_zone_id", "in", self.capture_zone_id.ids),
                ("product_type_id", "in", self.product_type_id.ids),
            ],
            order="date_from desc",
        )
        candidates_by_pair = {}
        for record in candidates:
            candidates_by_pair.setdefault(
                (record.capture_zone_id.id, record.product_type_id.id), []
            ).append(record)

        for origin in self:
            origin.status_id = False
            for record in candidates_by_pair.get(
                (origin.capture_zone_id.id, origin.product_type_id.id), []
            ):
                if record.date_from <= origin.capture_date and (
                    not record.date_to or record.date_to >= origin.capture_date
                ):
                    origin.status_id = record
                    break
