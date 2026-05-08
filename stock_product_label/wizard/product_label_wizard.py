# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, _
from odoo.exceptions import UserError

class ProductLabelLotWizard(models.TransientModel):
    _name = "product.label.lot.wizard"
    _inherit = "datamatrix.mh10.mixin"
    _description="product.label.lot.wizard"

    product_id = fields.Many2one("product.product", readonly=True, default=lambda self: self.env.context.get("default_product_id"))
    lot_id = fields.Many2one("stock.production.lot")

    def print_label_by_lot(self):
        if not self.product_id.barcode:
            raise UserError(_("Error, the product must have to a barcode"))
        return self.env.ref('stock_product_label.product_label_with_lot_report').report_action(self)
