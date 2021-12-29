# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html
from odoo import models


class SupplyCondition(models.Model):
    _name = "supply.condition"
    _inherit = ["model.code.mixin"]
    _description = "Supply Condition"
