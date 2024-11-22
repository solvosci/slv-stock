# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ls_default_one_line_product_id = fields.Many2one(
        related="company_id.ls_default_one_line_product_id",
        readonly=False,
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    ls_default_one_line_product_id = fields.Many2one(
        comodel_name="product.product",
        domain="[('type', '=', 'product')]",
        string="Default product in purchase for one line",
    )
