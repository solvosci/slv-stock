# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class SanitaryGuide(models.Model):
    _name = "sanitary.guide"
    _description = "Sanitary Guide (Documento de orixe)"
    _rec_name = "guide_number"
    _order = "issue_datetime desc, id desc"

    guide_number = fields.Char(
        string="Guide Number",
        required=True,
        index=True,
        help="Document number, e.g. 2026R000086454.",
    )

    api_recipient_vat = fields.Char(string="Recipient VAT", help="'cliente_nif'.")
    api_recipient_name = fields.Char(string="Recipient Name", help="'cliente_nombre'.")
    api_destination_type = fields.Char(string="Destination Type", help="'destino_tipo'.")

    issuer_name = fields.Char(string="Issuing Entity", help="'emisor_nombre'.")
    issuer_vat = fields.Char(string="Issuing Entity VAT", help="'emisor_cif'.")
    issuer_address = fields.Char(string="Issuing Entity Address", help="'emisor_direccion'.")
    issuer_phone = fields.Char(string="Issuing Entity Phone", help="'emisor_tfno'.")

    document_state = fields.Char(string="Document State", help="'estado', e.g. 'Confirmado'.")
    issue_datetime = fields.Datetime(string="Issue Date and Time", help="'fecha_emision'.")
    capture_date = fields.Date(string="Capture Date", help="'fecha_Recoleccion'.")
    registration_datetime = fields.Datetime(
        string="Registration Date and Time", help="'fecha_Registro'."
    )
    version_number = fields.Integer(string="Version", help="'intversion'.")
    production_method = fields.Char(string="Production Method", help="'metodo_produccion'.")
    is_registered = fields.Boolean(string="Registered", help="'registrado' == 'SI'.")

    # The API's own field names are the reverse of ours.
    capture_zone_raw_name = fields.Char(
        string="Capture Zone (as returned)", help="'zona_biotoxina_nombre'."
    )
    capture_zone_id = fields.Many2one(
        "intecmar.capture.zone",
        string="Capture Zone",
        help="Matched from capture_zone_raw_name's code. Left empty if no "
            "exact match is found.",
    )
    biotoxin_zone_status = fields.Char(
        string="Capture Zone Status (as returned)", help="'zona_biotoxina_estado'."
    )
    biological_zone_raw_name = fields.Char(
        string="Biological Zone (as returned)", help="'zona_captura_nombre'."
    )
    biological_zone_id = fields.Many2one(
        "intecmar.biological.zone",
        string="Biological Zone",
        help="Matched from biological_zone_raw_name's code. Left empty if "
            "no exact match is found.",
    )
    sanitary_qualification = fields.Char(
        string="Sanitary Qualification", help="'zona_captura_calificacion'."
    )

    last_fetch_error = fields.Text(
        string="Last Query Error",
        help="Set when the last attempt to query this guide from the API "
            "failed.",
    )
    line_ids = fields.One2many("sanitary.guide.line", "guide_id", string="Captures")
    move_line_ids = fields.One2many(
        "stock.move.line", "sanitary_guide_id", string="Receipt Lines"
    )
    lot_origin_ids = fields.One2many(
        "lot.capture.zone.origin", "sanitary_guide_id", string="Linked Lot Origins"
    )
    lot_count = fields.Integer(string="Lots", compute="_compute_lot_count")
    lots_to_review_count = fields.Integer(
        string="Lots to Review", compute="_compute_lot_count",
        help="Lots whose own zone(s) no longer match this guide's "
            "current data.",
    )

    _guide_number_unique = models.Constraint(
        "unique(guide_number)",
        "This sanitary guide number is already registered.",
    )

    @api.depends("lot_origin_ids.lot_id", "lot_origin_ids.needs_review")
    def _compute_lot_count(self):
        grouped = self.env["lot.capture.zone.origin"]._read_group(
            domain=[("sanitary_guide_id", "in", self.ids)],
            groupby=["sanitary_guide_id"],
            aggregates=["lot_id:count_distinct"],
        )
        lot_count_map = {guide.id: count for guide, count in grouped}
        to_review_grouped = self.env["lot.capture.zone.origin"]._read_group(
            domain=[("sanitary_guide_id", "in", self.ids), ("needs_review", "=", True)],
            groupby=["sanitary_guide_id"],
            aggregates=["lot_id:count_distinct"],
        )
        to_review_map = {guide.id: count for guide, count in to_review_grouped}
        for record in self:
            record.lot_count = lot_count_map.get(record.id, 0)
            record.lots_to_review_count = to_review_map.get(record.id, 0)

    def action_view_lots(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_production_lot_form"
        )
        action["domain"] = [("capture_origin_ids.sanitary_guide_id", "=", self.id)]
        action["context"] = {}
        return action

    def action_view_lots_to_review(self):
        self.ensure_one()
        lots = self.lot_origin_ids.filtered("needs_review").lot_id
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "stock.action_production_lot_form"
        )
        action["domain"] = [("id", "in", lots.ids)]
        action["context"] = {}
        return action

    @api.model
    def _match_zone_code(self, raw_name, zone_model):
        if not raw_name:
            return False
        code, _sep, name = raw_name.partition(" - ")
        code = code.strip()
        name = name.strip() or code
        if not code:
            return False
        zone = self.env[zone_model].search([("code", "=", code)], limit=1)
        if not zone:
            zone = self.env[zone_model].create({"code": code, "name": name})
        return zone.id

    def _fetch_from_api(self):
        self.ensure_one()
        try:
            vals, _pdf_base64 = self.env["sanitary.guide.sync"]._fetch_guide(self.guide_number)
        except UserError as exc:
            self.last_fetch_error = str(exc)
            raise
        vals["last_fetch_error"] = False
        vals["capture_zone_id"] = self._match_zone_code(
            vals.get("capture_zone_raw_name"), "intecmar.capture.zone"
        )
        vals["biological_zone_id"] = self._match_zone_code(
            vals.get("biological_zone_raw_name"), "intecmar.biological.zone"
        )
        self.write(vals)

    def action_refetch(self):
        for guide in self:
            guide._fetch_from_api()

    def action_download_pdf(self):
        self.ensure_one()
        _vals, pdf_base64 = self.env["sanitary.guide.sync"]._fetch_guide(self.guide_number)
        if not pdf_base64:
            raise UserError(self.env._(
                "The service did not return a PDF for this guide."
            ))
        attachment = self.env["ir.attachment"].create({
            "name": "%s.pdf" % self.guide_number,
            "type": "binary",
            "datas": pdf_base64,
            "res_model": self._name,
            "res_id": self.id,
            "mimetype": "application/pdf",
        })
        return {
            "type": "ir.actions.act_url",
            "url": "/web/content/%s?download=true" % attachment.id,
            "target": "self",
        }

    @api.model
    def _get_or_fetch(self, guide_number):
        guide = self.search([("guide_number", "=", guide_number)], limit=1)
        if guide and not guide.last_fetch_error:
            return guide
        if not guide:
            guide = self.create({"guide_number": guide_number})
        guide._fetch_from_api()
        return guide
