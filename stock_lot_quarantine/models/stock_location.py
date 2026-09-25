# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_purification_location = fields.Boolean(
        string="Purification/Quarantine Location",
        help="Marks this location as quarantine-side (a bin twin, or "
            "a warehouse's quarantine root).",
    )
    purification_mirror_location_id = fields.Many2one(
        "stock.location",
        string="Quarantine Twin",
        domain="[('is_purification_location', '=', True), ('usage', '=', 'internal')]",
        check_company=True,
        help="Quarantine twin of this location, where blocked lots "
            "are held. Created automatically if left empty.",
    )

    @api.constrains("purification_mirror_location_id", "is_purification_location")
    def _check_purification_mirror(self):
        for location in self:
            if location.is_purification_location and location.purification_mirror_location_id:
                raise ValidationError(_(
                    "%(location)s is a quarantine location and cannot "
                    "have its own quarantine twin.",
                    location=location.display_name,
                ))
            target = location.purification_mirror_location_id
            if not target:
                continue
            if not target.is_purification_location:
                raise ValidationError(_(
                    "%(target)s is set as the quarantine twin of "
                    "%(location)s but is not a Purification/Quarantine "
                    "Location.",
                    target=target.display_name,
                    location=location.display_name,
                ))
            other = self.search(
                [
                    ("purification_mirror_location_id", "=", target.id),
                    ("id", "!=", location.id),
                ],
                limit=1,
            )
            if other:
                raise ValidationError(_(
                    "%(target)s is already the quarantine twin of "
                    "%(other)s.",
                    target=target.display_name,
                    other=other.display_name,
                ))

    def _is_within(self, root):
        self.ensure_one()
        if not root or not root.parent_path or not self.parent_path:
            return False
        return self.parent_path.startswith(root.parent_path)

    def _get_or_create_quarantine_mirror(self):
        self.ensure_one()
        if self.is_purification_location:
            return self
        if self.purification_mirror_location_id:
            return self.purification_mirror_location_id

        warehouse = self.warehouse_id
        quarantine_root = warehouse.quarantine_location_id
        if not quarantine_root:
            return None
        if self._is_within(quarantine_root):
            return self

        mirror = self.env["stock.location"].create(
            {
                "name": self.name,
                "location_id": quarantine_root.id,
                "usage": "internal",
                "company_id": warehouse.company_id.id,
                "is_purification_location": True,
            }
        )
        self.purification_mirror_location_id = mirror.id
        return mirror

    def _get_purification_origin(self):
        self.ensure_one()
        return self.env["stock.location"].search(
            [("purification_mirror_location_id", "=", self.id)], limit=1
        )
