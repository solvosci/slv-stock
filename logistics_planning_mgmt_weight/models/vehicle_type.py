# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models

from odoo.addons.logistics_planning_base.models.logistics_schedule import (
    TRANSPORT_TYPE,
)


class VehicleType(models.Model):
    _inherit = "vehicle.type"

    ls_sale_transport_type = fields.Selection(
        selection=TRANSPORT_TYPE,
        default=TRANSPORT_TYPE[0][0],
        required=True,
        string="Transport Type",
    )
