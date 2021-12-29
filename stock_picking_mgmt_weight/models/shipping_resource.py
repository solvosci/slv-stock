# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class ShippingResource(models.Model):
    _name = "shipping.resource"
    _inherit = ["model.code.mixin"]
    _description = "Shipping Resource"
