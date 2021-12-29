# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    supply_condition_id = fields.Many2one(comodel_name="supply.condition")
    vehicle_type_id = fields.Many2one(comodel_name="vehicle.type")
