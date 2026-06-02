# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, _
from odoo.exceptions import UserError


class ProductProduct(models.Model):
    _name = "product.product"
    _inherit = ["product.product", "datamatrix.mh10.mixin"]

    def action_open_label_qr(self):
        if not self.barcode:
            raise UserError(_("Error, the product must have a barcode"))
        if self.tracking != 'none':
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.label.lot.wizard',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_product_id': self.id,
                }
            }
        else:
            return self.env.ref('stock_product_label.product_product_label_wo_lot_report').report_action(self)
