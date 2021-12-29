# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    shipping_resource_id = fields.Many2one(
        comodel_name="shipping.resource",
        default=lambda self: self.env["shipping.resource"].get_default(),
    )
