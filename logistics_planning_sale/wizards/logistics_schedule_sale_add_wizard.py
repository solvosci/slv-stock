# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.logistics_planning_base.models.logistics_schedule import PRICE_UNIT_TYPES


class LogisticsScheduleSaleAdd(models.TransientModel):
    _name = "logistics.schedule.sale.add.wizard"
    _description = "Logistics Schedule Add - Sale wizard"

    sale_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        required=True,
        readonly=True,
    )
    product_id = fields.Many2one(
        related="sale_line_id.product_id",
    )
    ls_count = fields.Integer(
        required=True,
        readonly=True,
        string="Current schedule count",
    )
    ls_new = fields.Integer(
        string="New schedules to be added",
        default=1,
    )
    logistics_price_unit_type = fields.Selection(
        selection=PRICE_UNIT_TYPES,
        required=True,
    )
    logistics_price_unit = fields.Float(digits="Product Price")
    currency_id = fields.Many2one("res.currency")

    def create_logistics_schedules(self):
        if self.ls_new <= 0:
            raise ValidationError(_(
                "Please fill a valid number of new schedules to be added (> 0)"
            ))
        ls_values = [
            self.sale_line_id._prepare_logistics_schedule()
            for i in range(0, self.ls_new)
        ]
        upd_values = {
            "logistics_price_unit_type": self.logistics_price_unit_type,
            "logistics_price_unit": self.logistics_price_unit,
        }
        for values in ls_values:
            values.update(upd_values)
        ls_ids = self.env["logistics.schedule"].sudo().create(ls_values)
        ls_ids._action_ready()
