# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import AccessError


class StockLot(models.Model):
    _inherit = "stock.lot"

    toxin_block_state = fields.Selection(
        [
            ("not_applicable", "Not Applicable / Exempt"),
            ("blocked", "Blocked (capture zone closed)"),
            ("released", "Released"),
        ],
        string="Toxin Block Status",
        default="not_applicable",
        tracking=True,
        help="This lot's own toxin block status.",
    )
    capture_origin_ids = fields.One2many(
        "lot.capture.zone.origin", "lot_id",
        string="Capture Origins",
        help="Capture Zone(s) and date(s) this lot's stock came from.",
    )
    toxin_block_reason = fields.Text(string="Toxin Block Reason")

    is_ready_for_sale = fields.Boolean(
        string="Ready for Sale",
        compute="_compute_is_ready_for_sale",
        store=True,
        help="True when neither the purification hold nor the toxin "
             "block is active.",
    )

    @api.depends("purification_state", "toxin_block_state")
    def _compute_is_ready_for_sale(self):
        for lot in self:
            purification_ok = lot.purification_state in (
                "released", "not_applicable",
            )
            toxin_ok = lot.toxin_block_state in ("released", "not_applicable")
            lot.is_ready_for_sale = purification_ok and toxin_ok

    def _evaluate_toxin_block(self):
        self.mapped("capture_origin_ids").sudo()._compute_status_id()
        for lot in self:
            if not lot.capture_origin_ids:
                lot._mark_toxin_exempt()
                continue

            reasons = []
            for origin in lot.capture_origin_ids.filtered(
                lambda x: x.status_id and x.status_id.blocks_extraction
            ):
                reasons.append(
                    "Capture Zone '%s' was reported as '%s' for product type "
                    "'%s' on %s."
                    % (origin.capture_zone_id.display_name,
                       origin.status_id.state_id.external_label,
                       origin.product_type_id.code, origin.capture_date)
                )

            if reasons:
                lot._start_toxin_block("\n".join(reasons))
            else:
                lot._mark_toxin_exempt()

    def _start_toxin_block(self, reason):
        self.ensure_one()
        self.write({
            "toxin_block_state": "blocked",
            "toxin_block_reason": reason,
        })
        self._send_stock_to_quarantine()

    def _mark_toxin_exempt(self):
        self.ensure_one()
        self.write({"toxin_block_state": "not_applicable"})
        self._try_release_from_quarantine()

    def action_manual_release_toxin_block(self):
        if not self.env.user.has_group("stock_lot_quarantine.group_purification_manager"):
            raise AccessError(
                "Only Purification managers can release a toxin block."
            )
        for lot in self.filtered(lambda l: l.toxin_block_state == "blocked"):
            lot.write({"toxin_block_state": "released"})
            lot._try_release_from_quarantine()

    def _release_stock_from_quarantine(self):
        for lot in self:
            lot.write({"purification_state": "released"})
            lot._try_release_from_quarantine()

    def _try_release_from_quarantine(self):
        self.ensure_one()
        self.invalidate_recordset(["is_ready_for_sale"])
        if not self.is_ready_for_sale:
            return  # still blocked by the other mechanism
        for quant in self.env["stock.quant"].search([
            ("lot_id", "=", self.id),
            ("location_id.is_purification_location", "=", True),
            ("quantity", ">", 0),
        ]).filtered(lambda q: q.available_quantity > 0):
            self._create_purification_transfer(
                quant.available_quantity,
                quant.location_id,
                quant.location_id._get_purification_origin(),
                "Toxin block release",
            )

    @api.model
    def _cron_release_purified_lots(self):
        res = super()._cron_release_purified_lots()
        for lot in self.search([("toxin_block_state", "=", "blocked")]):
            lot._send_stock_to_quarantine()
        return res
