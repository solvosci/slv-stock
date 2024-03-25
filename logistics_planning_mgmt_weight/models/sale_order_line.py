# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("vehicle_type_id")
    def _onchange_vehicle_type_id(self):
        if self.vehicle_type_id:
            self.ls_transport_type = self.vehicle_type_id.ls_sale_transport_type

    def _prepare_logistics_schedule(self):
        values = super()._prepare_logistics_schedule()
        values.update({
            "supply_condition_id": self.supply_condition_id.id or False,
        })
        return values
