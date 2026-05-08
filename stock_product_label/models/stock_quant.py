# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _name = "stock.quant"
    _inherit = ["stock.quant", "datamatrix.mh10.mixin"]

    def action_open_label_qr(self):
        for record in self.filtered(lambda x: not x.product_id.barcode):
            raise UserError(_("Error, the product %s must have to a barcode") % (record.product_id.name))
        return self.env.ref('stock_product_label.stock_quant_label_report').report_action(self)
