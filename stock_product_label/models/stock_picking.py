# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _name = "stock.picking"
    _inherit = ["stock.picking", "datamatrix.mh10.mixin"]

    def action_open_label_qr(self):
        for line in self.move_ids_without_package.filtered(lambda x: not x.product_id.barcode):
            raise UserError(_("Error, the product %s must have a barcode" % (line.product_id.name)))
        return self.env.ref('stock_product_label.stock_picking_label_report').report_action(self)
