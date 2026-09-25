# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    biological_zone_api_url = fields.Char(
        string="Biological Zone Classification API URL",
        config_parameter="stock_intecmar_biological_zone.biological_zone_api_url",
        default="https://www.intecmar.gal/Api/EstadoZonasProducion/ClasificacionMicrobioloxicaZonas",
        help="Endpoint the biological classification sync downloads from.",
    )
    biological_zone_last_update_date = fields.Char(
        string="Last Synced Biological Dataset Timestamp",
        config_parameter="stock_intecmar_biological_zone.biological_zone_last_update_date",
        help="Informational only, from the last successful sync.",
    )
