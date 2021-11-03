# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    picking_partner_id = fields.Many2one(
        related="picking_id.partner_id",
        string="Partner",
        store=True
    )
