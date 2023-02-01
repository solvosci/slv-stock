# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class PhapQtyEditWizard(models.TransientModel):
    _name = "phap.qty.edit.wizard"
    _description = "PHAP Quantity Edit Wizard"

    phap_id = fields.Many2one("product.history.average.price", readonly=True)
    location_id = fields.Many2one(related="phap_id.warehouse_id.lot_stock_id")
    stock_quantity = fields.Float(
        related="phap_id.stock_quantity",
        string="Current stock quantity",
    )
    stock_quantity_new = fields.Float(
        digits="Product Unit of Measure",
        required=True,
        string="New stock quantity",
    )

    def action_confirm(self):
        self.ensure_one()
        self.phap_id._update_quantity(
            self.location_id, self.stock_quantity_new
        )
