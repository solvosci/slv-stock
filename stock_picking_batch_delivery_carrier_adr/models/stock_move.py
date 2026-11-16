# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models, fields, api


class StockMove(models.Model):
    _inherit="stock.move"

    package_qty = fields.Integer()
    packages_weight = fields.Float(
        compute="_compute_packages_weight",
        store=True
        )
    is_dangerous = fields.Boolean(
        related="product_id.is_dangerous"
        )

    @api.depends('quantity', 'product_id.weight')
    def _compute_packages_weight(self):
        for record in self:
            record.packages_weight = record.quantity * record.product_id.weight
