# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sanitary_guide_api_url = fields.Char(
        string="Sanitary Guide API URL",
        config_parameter="stock_sanitary_guide.api_url",
        help="WSDL endpoint of the Xunta de Galicia destinosService.",
    )
    sanitary_guide_api_auth_user = fields.Char(
        string="Sanitary Guide API HTTP Auth User",
        config_parameter="stock_sanitary_guide.api_auth_user",
    )
    sanitary_guide_api_auth_password = fields.Char(
        string="Sanitary Guide API HTTP Auth Password",
        config_parameter="stock_sanitary_guide.api_auth_password",
    )
    sanitary_guide_api_user = fields.Char(
        string="Sanitary Guide API User",
        config_parameter="stock_sanitary_guide.api_user",
    )
    sanitary_guide_api_password = fields.Char(
        string="Sanitary Guide API Password",
        config_parameter="stock_sanitary_guide.api_password",
    )
