# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _prepare_logistics_schedule(self):
        values = super()._prepare_logistics_schedule()
        values.update({
            "carrier_id": self.order_id.carrier_id.id,
            # TODO remove if computed
            "effective_carrier_id": self.order_id.carrier_id.id,
            "supply_condition_id": self.supply_condition_id.id or False,
        })
        return values
