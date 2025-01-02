# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    lot_stock_total_quantities = fields.Boolean(
        string="Ensure that total stock quantity is delivered",
        compute="_compute_lot_stock_total_quantities",
        store=True,
        readonly=False,
    )

    @api.depends("tracking")
    def _compute_lot_stock_total_quantities(self):
        self.filtered(lambda x: x.tracking != "lot").update({
            "lot_stock_total_quantities": False,
        })
