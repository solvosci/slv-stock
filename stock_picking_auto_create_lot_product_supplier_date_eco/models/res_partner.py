# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import fields, models


class ResPartnerTemplate(models.Model):
    _inherit = "res.partner"

    exception_eco_product_ids = fields.Many2many(
        "product.template", 
        string="Exception ECO Products"
    )

    exception_eco_product_readonly = fields.Boolean(
        compute="_compute_exception_eco_product_readonly",
    )

    def _compute_exception_eco_product_readonly(self):
        is_readonly = not self.env.user.has_group("stock.group_stock_manager")
        for record in self:
            record.exception_eco_product_readonly = is_readonly
