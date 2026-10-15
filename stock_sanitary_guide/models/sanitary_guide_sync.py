# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

import logging
from datetime import date, datetime

from lxml import etree

from odoo import api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


def _parse_dt(value, fmt):
    if not value:
        return False
    try:
        return datetime.strptime(value, fmt)
    except ValueError:
        _logger.warning("Sanitary Guide API: could not parse date %r (expected %s)", value, fmt)
        return False


class SanitaryGuideSync(models.AbstractModel):
    _name = "sanitary.guide.sync"
    _description = "Sanitary Guide Query"

    def _get_client(self):
        url = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_url")
        auth_user = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_auth_user")
        auth_password = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_auth_password")
        if not url or not auth_user or not auth_password:
            raise UserError(self.env._(
                "The Sanitary Guide API is not configured."
            ))
        import requests
        from zeep import Client
        from zeep.transports import Transport

        session = requests.Session()
        session.auth = (auth_user, auth_password)
        return Client(wsdl=url, transport=Transport(session=session))

    def _get_document_credentials(self):
        user = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_user")
        password = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_password")
        if not user or not password:
            raise UserError(self.env._(
                "The Sanitary Guide API is not configured. Set the URL "
                "and both sets of credentials in Settings > Inventory > "
                "Sanitary Guide (Pesca de Galicia)."
            ))
        return user, password

    @api.model
    def _cron_sync_zone_catalog(self):
        client = self._get_client()
        user, password = self._get_document_credentials()
        from zeep.exceptions import Fault

        try:
            biotoxina = client.service.metDetalleZonasBiotoxinaVixentes(
                arg0={"nombreUsuario": user, "claveUsuario": password}
            )
            microbioloxica = client.service.metZonasClasificacionMicrobioloxicaVixentes(
                arg0={"nombreUsuario": user, "claveUsuario": password}
            )
        except Fault as exc:
            _logger.error("Xunta zone catalog sync failed: %s", exc)
            return
        except Exception as exc:
            _logger.error("Xunta zone catalog sync failed: %s", exc)
            return

        biotoxina_node = getattr(biotoxina, "_value_1", biotoxina)
        if biotoxina_node is not None and etree.QName(biotoxina_node.tag).localname == "error":
            _logger.error(
                "Xunta zone catalog sync failed (metDetalleZonasBiotoxinaVixentes): %s",
                biotoxina_node.get("mensaje"),
            )
            return
        microbioloxica_node = getattr(microbioloxica, "_value_1", microbioloxica)
        if microbioloxica_node is not None and etree.QName(microbioloxica_node.tag).localname == "error":
            _logger.error(
                "Xunta zone catalog sync failed (metZonasClasificacionMicrobioloxicaVixentes): %s",
                microbioloxica_node.get("mensaje"),
            )
            return

        self._sync_capture_zone_catalog(biotoxina_node)
        self._sync_biological_zone_catalog(microbioloxica_node)

    def _sync_capture_zone_catalog(self, node):
        if node is None:
            return

        entries = []
        for zona_node in node.findall("{*}zona"):
            codigo = zona_node.get("codigo") or ""
            nombre = zona_node.get("nombre") or ""
            zone_code, _sep, type_code = codigo.partition("@") # "ZONACODE@TYPECODE"
            if not zone_code or not type_code:
                continue
            zone_name = nombre.split(" - ", 1)[1] if " - " in nombre else (nombre or zone_code)
            entries.append((zone_code, type_code, zone_name))
        if not entries:
            return

        zones_by_code = {
            z.code: z for z in self.env["intecmar.capture.zone"].search([("code", "in", list({e[0] for e in entries}))])
        }
        missing_zone_vals = []
        for zone_code, _type_code, zone_name in entries:
            if zone_code not in zones_by_code:
                missing_zone_vals.append({"code": zone_code, "name": zone_name})
                zones_by_code[zone_code] = None  
        if missing_zone_vals:
            for zone in self.env["intecmar.capture.zone"].create(missing_zone_vals):
                zones_by_code[zone.code] = zone

        types_by_code = {
            t.code: t for t in self.env["intecmar.capture.product.type"].search([("code", "in", list({e[1] for e in entries}))])
        }
        missing_type_vals = []
        for _zone_code, type_code, _zone_name in entries:
            if type_code not in types_by_code:
                missing_type_vals.append({"code": type_code, "name": type_code})
                types_by_code[type_code] = None
        if missing_type_vals:
            for ptype in self.env["intecmar.capture.product.type"].create(missing_type_vals):
                types_by_code[ptype.code] = ptype

        existing_pairs = {
            (h.capture_zone_id.id, h.product_type_id.id)
            for h in self.env["intecmar.capture.zone.status.history"].search([
                ("capture_zone_id", "in", [z.id for z in zones_by_code.values()]),
                ("product_type_id", "in", [t.id for t in types_by_code.values()]),
            ])
        }
        undetermined = self.env.ref("stock_sanitary_guide.capture_zone_state_undetermined")
        new_history_vals = []
        for zone_code, type_code, _zone_name in entries:
            pair = (zones_by_code[zone_code].id, types_by_code[type_code].id)
            if pair in existing_pairs:
                continue
            existing_pairs.add(pair)
            new_history_vals.append({
                "capture_zone_id": pair[0],
                "product_type_id": pair[1],
                "state_id": undetermined.id,
                "date_from": date(2000, 1, 1),
                "report_type": "other",
                "source": "guide",
                "notes": "Created from the Xunta zone catalog "
                    "(metDetalleZonasBiotoxinaVixentes)",
            })
        if new_history_vals:
            self.env["intecmar.capture.zone.status.history"].create(new_history_vals)

    def _sync_biological_zone_catalog(self, node):
        if node is None:
            return

        entries = []
        for zona_node in node.findall("{*}zona"):
            codigo = zona_node.get("codigo") or ""
            nombre = zona_node.get("nombre") or ""
            _type_code, _sep, zone_code = codigo.partition("@") # "TYPECODE@ZONACODE"
            if not zone_code:
                continue
            zone_name = nombre.split(" - ", 1)[1] if " - " in nombre else (nombre or zone_code)
            entries.append((zone_code, zone_name))
        if not entries:
            return

        BiologicalZone = self.env["intecmar.biological.zone"]
        existing_codes = set(
            BiologicalZone.search([("code", "in", list({e[0] for e in entries}))]).mapped("code")
        )
        new_zone_vals = []
        for zone_code, zone_name in entries:
            if zone_code in existing_codes:
                continue
            existing_codes.add(zone_code)
            new_zone_vals.append({"code": zone_code, "name": zone_name})
        if new_zone_vals:
            BiologicalZone.create(new_zone_vals)

    def _fetch_guide(self, guide_number):
        url = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_url")
        auth_user = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_auth_user")
        auth_password = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_auth_password")
        user = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_user")
        password = self.env["ir.config_parameter"].sudo().get_param("stock_sanitary_guide.api_password")
        if not url or not auth_user or not auth_password or not user or not password:
            raise UserError(self.env._(
                "The Sanitary Guide API is not configured."
            ))

        import requests
        from zeep import Client
        from zeep.exceptions import Fault
        from zeep.transports import Transport

        try:
            session = requests.Session()
            session.auth = (auth_user, auth_password)
            client = Client(wsdl=url, transport=Transport(session=session))
            response = client.service.metConsultaDocumentoRexistroParticular(
                arg0={
                    "codigoDocumento": guide_number,
                    "nombreUsuario": user,
                    "claveUsuario": password,
                }
            )
        except Fault as exc:
            raise UserError(self.env._(
                "The Sanitary Guide service returned an error: %s", exc
            )) from exc
        except Exception as exc:
            _logger.error("Sanitary Guide API call failed: %s", exc)
            raise UserError(self.env._(
                "Could not reach the Sanitary Guide service."
            )) from exc

        node = getattr(response, "_value_1", response)
        if node is None:
            raise UserError(self.env._(
                "The Sanitary Guide service returned an empty response "
                "for document %s.", guide_number
            ))

        tag = etree.QName(node.tag).localname
        if tag == "error":
            raise UserError(node.get("mensaje") or self.env._(
                "The Sanitary Guide service rejected the request."
            ))
        if tag != "documento":
            raise UserError(self.env._(
                "Unexpected response from the Sanitary Guide service "
                "(got '%s', expected 'documento').", tag
            ))

        vals = {
            "guide_number": node.get("codigo") or guide_number,
            "api_recipient_vat": node.get("cliente_nif"),
            "api_recipient_name": node.get("cliente_nombre"),
            "api_destination_type": node.get("destino_tipo"),
            "issuer_name": node.get("emisor_nombre"),
            "issuer_vat": node.get("emisor_cif"),
            "issuer_address": node.get("emisor_direccion"),
            "issuer_phone": node.get("emisor_tfno"),
            "document_state": node.get("estado"),
            "issue_datetime": _parse_dt(node.get("fecha_emision"), "%d/%m/%Y %H:%M:%S"),
            "capture_date": _parse_dt(node.get("fecha_Recoleccion"), "%d/%m/%Y"),
            "registration_datetime": _parse_dt(node.get("fecha_Registro"), "%d/%m/%Y %H:%M:%S"),
            "version_number": int(node.get("intversion")) if node.get("intversion") else False,
            "production_method": node.get("metodo_produccion"),
            "is_registered": (node.get("registrado") or "").strip().upper() == "SI",
            # The API's "zona_captura" is OUR biological zone, and its "zona_biotoxina" is OUR
            # capture zone. This is intentional, not swapped by mistake.
            "biological_zone_raw_name": node.get("zona_captura_nombre"),
            "sanitary_qualification": node.get("zona_captura_calificacion"),
            "capture_zone_raw_name": node.get("zona_biotoxina_nombre"),
            "biotoxin_zone_status": node.get("zona_biotoxina_estado"),
        }

        line_vals = []
        pdf_base64 = None
        for child in node:
            child_tag = etree.QName(child.tag).localname
            if child_tag == "especie":
                kilos = child.get("kilos") or "0"
                line_vals.append({
                    "fao_code": child.get("fao"),
                    "quantity_kg": float(kilos.replace(",", ".")),
                })
            elif child_tag == "pdf":
                pdf_base64 = child.text
        if line_vals:
            vals["line_ids"] = [(0, 0, vals_line) for vals_line in line_vals]

        return vals, pdf_base64
