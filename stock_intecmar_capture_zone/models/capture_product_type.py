# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ShellfishCaptureProductType(models.Model):
    _name = "intecmar.capture.product.type"
    _description = "Capture Product Type (INTECMAR)"
    _order = "code"

    code = fields.Char(
        string="Code",
        required=True,
        index=True,
        help="Product type code as published by INTECMAR.",
    )
    name = fields.Char(string="Name", required=True)

    zone_count = fields.Integer(
        string="Capture Zones",
        compute="_compute_zone_count",
        help="Capture Zones associated with this product type.",
    )

    _code_unique = models.Constraint(
        "unique(code)",
        "This product type code is already registered.",
    )

    @api.depends("name", "code")
    def _compute_display_name(self):
        for product_type in self:
            product_type.display_name = "%s (%s)" % (
                product_type.name, product_type.code,
            )

    def _compute_zone_count(self):
        grouped = self.env["intecmar.capture.zone.status.history"]._read_group(
            domain=[("product_type_id", "in", self.ids)],
            groupby=["product_type_id"],
            aggregates=["capture_zone_id:count_distinct"],
        )
        zone_count_map = {group[0].id: group[1] for group in grouped}
        for product_type in self:
            product_type.zone_count = zone_count_map.get(product_type.id, 0)

    def action_view_zones(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock_intecmar_capture_zone.action_capture_zone"
        )
        action["domain"] = [("status_ids.product_type_id", "=", self.id)]
        action["context"] = {}
        return action
