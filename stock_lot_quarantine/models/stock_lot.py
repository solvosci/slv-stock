# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    purification_state = fields.Selection(
        [
            ("not_applicable", "Not Applicable / Exempt"),
            ("blocked", "Blocked (in quarantine)"),
            ("released", "Released"),
        ],
        string="Purification State",
        default="not_applicable",
        tracking=True,
        help="Current purification status of this lot.",
    )
    purification_start_date = fields.Datetime(string="Quarantine Start")
    purification_hours = fields.Float(
        string="Quarantine Hours Applied",
        help="Quarantine hours applied to this lot, copied from the "
            "product at reception.",
    )
    purification_release_date = fields.Datetime(
        string="Expected Release",
        compute="_compute_purification_release_date",
        store=True,
        help="Date when the lot is automatically released.",
    )
    purification_time_remaining = fields.Char(
        string="Time Remaining",
        compute="_compute_purification_time_remaining",
    )

    @api.depends("purification_start_date", "purification_hours")
    def _compute_purification_release_date(self):
        for lot in self:
            if lot.purification_start_date and lot.purification_hours:
                lot.purification_release_date = fields.Datetime.add(
                    lot.purification_start_date,
                    hours=lot.purification_hours,
                )
            else:
                lot.purification_release_date = False

    @api.depends("purification_state", "purification_release_date")
    def _compute_purification_time_remaining(self):
        now = fields.Datetime.now()
        for lot in self:
            if (
                lot.purification_state != "blocked"
                or not lot.purification_release_date
            ):
                lot.purification_time_remaining = "-"
                continue
            delta = lot.purification_release_date - now
            if delta.total_seconds() <= 0:
                lot.purification_time_remaining = "Pending release"
            else:
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                lot.purification_time_remaining = "%dh %dm" % (hours, minutes)

    def write(self, vals):
        leaving_quarantine = self.env["stock.lot"]
        newly_blocked = self.env["stock.lot"]
        new_state = vals.get("purification_state")
        if new_state in ("released", "not_applicable"):
            leaving_quarantine = self.filtered(
                lambda lot: lot.purification_state == "blocked"
            )
        elif new_state == "blocked":
            newly_blocked = self.filtered(
                lambda lot: lot.purification_state != "blocked"
            )
        res = super().write(vals)

        if new_state is None and (
            "purification_start_date" in vals or "purification_hours" in vals
        ):
            now = fields.Datetime.now()
            for lot in self.filtered(lambda x: x.purification_release_date):
                if (
                    lot.purification_state != "blocked"
                    and lot.purification_release_date > now
                ):
                    lot.write({"purification_state": "blocked"})
                elif (
                    lot.purification_state == "blocked"
                    and lot.purification_release_date <= now
                ):
                    lot.write({"purification_state": "released"})

        for lot in leaving_quarantine:
            lot._release_stock_from_quarantine()
        for lot in newly_blocked:
            lot._send_stock_to_quarantine()
        return res

    def _start_quarantine(self, hours):
        self.ensure_one()
        self.write(
            {
                "purification_state": "blocked",
                "purification_start_date": fields.Datetime.now(),
                "purification_hours": hours,
            }
        )

    def _mark_exempt(self):
        self.write({"purification_state": "not_applicable"})

    def _create_purification_transfer(
        self, quantity, source_location, dest_location, origin_label
    ):
        self.ensure_one()
        if not dest_location or source_location == dest_location:
            return None

        env = self.env
        picking = env["stock.picking"].create(
            {
                "picking_type_id": source_location.warehouse_id.int_type_id.id,
                "location_id": source_location.id,
                "location_dest_id": dest_location.id,
                "origin": "%s - Lot %s" % (origin_label, self.name),
            }
        )
        env["stock.move"].create(
            {
                "product_id": self.product_id.id,
                "product_uom_qty": quantity,
                "product_uom": self.product_id.uom_id.id,
                "picking_id": picking.id,
                "location_id": source_location.id,
                "location_dest_id": dest_location.id,
            }
        )
        picking.action_confirm()
        picking.action_assign()
        picking.move_line_ids.write({"lot_id": self.id, "quantity": quantity})
        picking.button_validate()
        return picking

    def _release_stock_from_quarantine(self):
        self.ensure_one()
        for quant in self.env["stock.quant"].search(
            [
                ("lot_id", "=", self.id),
                ("location_id.is_purification_location", "=", True),
                ("quantity", ">", 0),
            ]
        ).filtered(lambda q: q.available_quantity > 0):
            self._create_purification_transfer(
                quant.available_quantity,
                quant.location_id,
                quant.location_id._get_purification_origin(),
                "Purification release",
            )

    def _send_stock_to_quarantine(self):
        self.ensure_one()
        for quant in self.env["stock.quant"].search(
            [
                ("lot_id", "=", self.id),
                ("location_id.usage", "=", "internal"),
                ("location_id.is_purification_location", "=", False),
                ("quantity", ">", 0),
            ]
        ).filtered(
            lambda q: q.location_id._is_within(q.location_id.warehouse_id.lot_stock_id)
            and q.available_quantity > 0
        ):
            mirror_location = quant.location_id._get_or_create_quarantine_mirror()
            if not mirror_location:
                continue
            self._create_purification_transfer(
                quant.available_quantity, quant.location_id, mirror_location, "Quarantine intake"
            )

    @api.model
    def _cron_release_purified_lots(self):
        self.search(
            [
                ("purification_state", "=", "blocked"),
                ("purification_release_date", "<=", fields.Datetime.now()),
            ]
        ).write({"purification_state": "released"})

        self.search(
            [
                ("purification_state", "=", "blocked"),
                ("purification_hours", "=", 0),
            ]
        ).write({"purification_state": "not_applicable"})

        for lot in self.search([("purification_state", "=", "blocked")]):
            lot._send_stock_to_quarantine()
