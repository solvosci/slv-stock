# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_compare


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _get_available_quantity_complete_lot(self):
        self.ensure_one()
        quant = (
            self.lot_id
            and self.lot_id.quant_ids.filtered(
                lambda x: x.location_id == self.location_id
            )
        )
        return quant and quant.quantity or 0.0
    
    def _action_done(self):
        sml_to_check_ids = self.filtered(
            lambda x: x.picking_code == "outgoing"
            and x.product_id.lot_stock_total_quantities
        )
        for sml in sml_to_check_ids:
            available_qty = sml._get_available_quantity_complete_lot()
            if float_compare(
                sml.qty_done,
                available_qty,
                precision_rounding=sml.product_id.uom_id.rounding or 0.001
            ) != 0:
                raise ValidationError(_(
                    "Done quantity for %s with lot %s doesn't match available"
                    " stock (%.3f != %.3f), please check"
                ) % (
                    sml.product_id.display_name,
                    sml.lot_id.name,
                    sml.qty_done,
                    available_qty,
                ))
        super()._action_done()
