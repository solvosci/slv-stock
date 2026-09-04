# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    toxin_zone_intecmar_url = fields.Char(
        string="INTECMAR Zone Status API URL",
        config_parameter="stock_intecmar_capture_zone.toxin_zone_intecmar_url",
        default="https://www.intecmar.gal/Api/EstadoZonasProducion/EstadoZonasBiotoxinas",
        help="Endpoint the sync downloads from.",
    )
    toxin_zone_last_update_date = fields.Char(
        string="Last Synced Dataset Timestamp",
        config_parameter="stock_intecmar_capture_zone.toxin_zone_last_update_date",
        help="Informational only, from the last successful sync.",
    )
