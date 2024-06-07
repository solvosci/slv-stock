# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    warehouse_valuation_close_date = fields.Date(
        related="company_id.warehouse_valuation_close_date",
        readonly=False,
    )

    # TODO checks
    # - Not in the future (not too close to current date, even in the past?)
