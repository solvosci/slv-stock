# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    warehouse_valuation = fields.Boolean(string="Valuation by warehouse and with daily historical average")
