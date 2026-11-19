# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from datetime import datetime, timedelta

import requests

from odoo import api, models

_logger = logging.getLogger(__name__)


class ShellfishIntecmarSync(models.AbstractModel):
    _name = "intecmar.sync"
    _description = "INTECMAR Bulletin Sync"

    @api.model
    def _cron_sync_intecmar_zone_status(self):
        self._run_sync()

    @api.model
    def _run_sync(self):
        return self._fetch_and_sync_dataset(
            label="INTECMAR zone status",
            url=self.env["ir.config_parameter"].sudo().get_param("stock_intecmar_capture_zone.toxin_zone_intecmar_url"),
            last_update_param="stock_intecmar_capture_zone.toxin_zone_last_update_date",
            entries_key="estadoZonas",
            process=lambda entries: self._sync_status_history(
                entries,
                self._sync_zones(entries),
                self._sync_product_types(entries),
                self._sync_state_mappings(entries),
            ),
        )

    def _fetch_and_sync_dataset(self, label, url, last_update_param, entries_key, process):
        if not url:
            _logger.info("%s sync: no API URL configured, skipping.", label)
            return None
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException as exc:
            _logger.error(
                "Failed to download %s from %s: %s", label, url, exc,
            )
            return None

        try:
            payload = response.json()
        except ValueError:
            _logger.error("%s response was not valid JSON.", label)
            return None

        update_date = payload.get("dataActualizacion")
        if update_date and update_date == self.env["ir.config_parameter"].sudo().get_param(last_update_param):
            _logger.info(
                "%s sync: dataset unchanged since last sync (%s), "
                "nothing to do.", label, update_date,
            )
            return None

        entries = payload.get(entries_key, [])
        if not entries:
            _logger.warning(
                "%s endpoint returned no entries -- the API format may "
                "have changed.", label,
            )
            return None

        result = process(entries)

        if update_date:
            self.env["ir.config_parameter"].sudo().set_param(last_update_param, update_date)
        return result

    def _sync_state_mappings(self, entries):
        Mapping = self.env["intecmar.capture.zone.state.mapping"]
        labels = {entry["estado"] for entry in entries}

        by_label = {
            mapping.external_label: mapping
            for mapping in Mapping.search([("external_label", "in", list(labels))])
        }

        new_labels = [label for label in labels if label not in by_label]
        if new_labels:
            _logger.warning(
                "INTECMAR sync: %d new state wording(s) not yet mapped, "
                "registered as blocking extraction by default -- review "
                "and correct if needed: %s",
                len(new_labels), new_labels,
            )
        for mapping in Mapping.create([
            {"external_label": label} for label in new_labels
        ]):
            by_label[mapping.external_label] = mapping
        return by_label

    def _sync_zones(self, entries):
        Zone = self.env["intecmar.capture.zone"]
        names_by_code = {entry["codigo"]: entry["nome"] for entry in entries}

        by_code = {
            zone.code: zone
            for zone in Zone.search([("code", "in", list(names_by_code))])
        }

        for zone in Zone.create([
            {"code": code, "name": name}
            for code, name in names_by_code.items()
            if code not in by_code
        ]):
            by_code[zone.code] = zone
        return by_code

    def _sync_product_types(self, entries):
        ProductType = self.env["intecmar.capture.product.type"]
        codes = {entry["tipo"] for entry in entries}

        by_code = {
            ptype.code: ptype
            for ptype in ProductType.search([("code", "in", list(codes))])
        }

        for ptype in ProductType.create([
            {"code": code, "name": code}
            for code in codes
            if code not in by_code
        ]):
            by_code[ptype.code] = ptype
        return by_code

    def _sync_status_history(self, entries, zones_by_code, types_by_code, mappings_by_label):
        existing = self.env["intecmar.capture.zone.status.history"].search(
            [
                ("capture_zone_id", "in", [zones_by_code[e["codigo"]].id for e in entries]),
                ("product_type_id", "in", [types_by_code[e["tipo"]].id for e in entries]),
            ],
            order="date_from desc",
        )
        last_by_pair = {}
        for record in existing:
            last_by_pair.setdefault((record.capture_zone_id.id, record.product_type_id.id), record)

        new_vals_list = []
        for entry in entries:
            effective_date = datetime.fromisoformat(
                entry["dataSituacionAdministrativa"]
            ).date()

            last = last_by_pair.get((zones_by_code[entry["codigo"]].id, types_by_code[entry["tipo"]].id))
            if last and last.date_from == effective_date:
                continue  

            if last and not last.date_to:
                last.date_to = effective_date - timedelta(days=1)

            new_vals_list.append({
                "capture_zone_id": zones_by_code[entry["codigo"]].id,
                "product_type_id": types_by_code[entry["tipo"]].id,
                "state_id": mappings_by_label[entry["estado"]].id,
                "date_from": effective_date,
                "report_type": "intecmar_bulletin",
                "source": "automatic",
            })

        return self.env["intecmar.capture.zone.status.history"].create(new_vals_list) if new_vals_list else self.env["intecmar.capture.zone.status.history"]
