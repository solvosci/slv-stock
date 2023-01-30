# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models


class PhapPriceEditWizard(models.TransientModel):
    _name = "phap.price.edit.wizard"
    _description = "PHAP Price Edit Wizard"

    phap_id = fields.Many2one("product.history.average.price", readonly=True)
    currency_id = fields.Many2one(related="phap_id.currency_id")
    average_price = fields.Monetary(
        related="phap_id.average_price",
        string="Current average price",
    )
    average_price_new = fields.Monetary(string="New average price")

    def action_confirm(self):
        self.ensure_one()
        self.phap_id.sudo().average_price_edit = self.average_price_new
