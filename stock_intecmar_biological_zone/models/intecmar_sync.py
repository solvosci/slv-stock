# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models


class ShellfishIntecmarSync(models.AbstractModel):
    _inherit = "intecmar.sync"

    @api.model
    def _cron_sync_intecmar_zone_status(self):
        super()._cron_sync_intecmar_zone_status()
        self._run_biological_sync()

    @api.model
    def _run_biological_sync(self):
        return self._fetch_and_sync_dataset(
            label="Biological zone classification",
            url=self.env["ir.config_parameter"].sudo().get_param("stock_intecmar_biological_zone.biological_zone_api_url"),
            last_update_param="stock_intecmar_biological_zone.biological_zone_last_update_date",
            entries_key="clasificacionZonas",
            process=self._sync_biological_zones,
        )

    def _sync_biological_zones(self, entries):
        zones_by_code = self._sync_biological_zone_identities(entries)
        self._sync_biological_zone_lines(entries, zones_by_code)

    def _sync_biological_zone_identities(self, entries):
        Classification = self.env["intecmar.biological.zone"]

        names_by_code = {entry["codigo"]: entry["nome"] for entry in entries}
        by_code = {
            record.code: record
            for record in Classification.search([
                ("code", "in", list(names_by_code))
            ])
        }
        for code, name in names_by_code.items():
            record = by_code.get(code)
            if record:
                if record.name != name:
                    record.name = name
            else:
                by_code[code] = Classification.create(
                    {"code": code, "name": name}
                )

        gone = Classification.search([("code", "not in", list(names_by_code))])
        gone.unlink()
        return by_code

    def _sync_biological_zone_lines(self, entries, zones_by_code):
        raw_lines = [
            {
                "code": entry["codigo"],
                "state": entry.get("estado"),
                "capture_zone_code": rel["codigoZonaBiotoxinas"],
                "type_code": rel["tipoZonaBiotoxinas"],
            }
            for entry in entries
            for rel in entry.get("relacionsZonasBiotoxinas", [])
        ]

        type_codes = {line["type_code"] for line in raw_lines}
        types_by_code = {
            ptype.code: ptype
            for ptype in self.env["intecmar.capture.product.type"].search([("code", "in", list(type_codes))])
        }
        for ptype in self.env["intecmar.capture.product.type"].create([
            {"code": code, "name": code}
            for code in type_codes
            if code not in types_by_code
        ]):
            types_by_code[ptype.code] = ptype

        capture_zone_codes = {line["capture_zone_code"] for line in raw_lines}
        capture_zones_by_code = {
            zone.code: zone
            for zone in self.env["intecmar.capture.zone"].search([("code", "in", list(capture_zone_codes))])
        }
        raw_lines = [
            line for line in raw_lines
            if line["capture_zone_code"] in capture_zones_by_code
        ]

        existing_by_key = {
            (
                line.biological_zone_id.id,
                line.capture_zone_id.id,
                line.product_type_id.id,
            ): line
            for line in self.env["intecmar.biological.zone.line"].search([])
        }
        seen_keys = set()

        for line in raw_lines:
            biological_id = zones_by_code[line["code"]].id
            capture_zone_id = capture_zones_by_code[line["capture_zone_code"]].id
            type_id = types_by_code[line["type_code"]].id
            key = (biological_id, capture_zone_id, type_id)
            seen_keys.add(key)
            vals = {
                "biological_zone_id": biological_id,
                "capture_zone_id": capture_zone_id,
                "product_type_id": type_id,
                "state": line["state"],
            }
            record = existing_by_key.get(key)
            if record:
                record.write(vals)
            else:
                existing_by_key[key] = self.env["intecmar.biological.zone.line"].create(vals)

        gone_keys = set(existing_by_key) - seen_keys
        if gone_keys:
            self.env["intecmar.biological.zone.line"].browse([
                existing_by_key[key].id for key in gone_keys
            ]).unlink()
