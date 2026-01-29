# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = "stock.move"

    button_complete_lot_qty_invisible = fields.Boolean(
        compute="_compute_button_complete_lot_qty_invisible",
    )
    
    @api.depends(
        "state",
        "product_id.lot_stock_total_quantities",
        "picking_code",
    )
    def _compute_button_complete_lot_qty_invisible(self):
        field_invisible_sm_ids = self.filtered(
            lambda x: x.state in ["done", "cancel"]
            # or x.is_locked
            # or not x.lot_id
            or not x.product_id.lot_stock_total_quantities
            or x.picking_code != "outgoing"
        )
        field_invisible_sm_ids.update({
            "button_complete_lot_qty_invisible": True,
        })
        (self - field_invisible_sm_ids).update({
            "button_complete_lot_qty_invisible": False,
        })
    
    def button_complete_lot_qty(self):
        self.ensure_one()
        if not self.move_line_ids:
            raise ValidationError(_(
                "There are not lots selected for this move,"
                " please first select some"
            ))
        sml_wo_lot_ids = self.move_line_ids.filtered(lambda x: not x.lot_id)
        if len(sml_wo_lot_ids) > 0:
            raise ValidationError(_(
                "There are at least one stock move line without lot selected,"
                " please check"
            ))
        # Check that every move line lot is unique and find which are duplicated
        lot_list = self.move_line_ids.mapped("lot_id")
        if len(lot_list) < len(self.move_line_ids):
            repeated_lots = []
            for lot in lot_list:
                if len(self.move_line_ids.filtered(lambda x: x.lot_id == lot)) > 1:
                    repeated_lots.append(lot.name)
            raise ValidationError(
                _(
                    "There are lot(s) duplicated, please remove duplicated.\n\n"
                    "Repeated lots: %s"
                ) % ", ".join(repeated_lots)
            )
        # TODO ensure right unit of measure
        for ml in self.move_line_ids:
            available_qty = ml._get_available_quantity_complete_lot()
            # TODO float_compare?
            if available_qty <= 0.0:
                raise ValidationError(_(
                    "There's no quantity available for lot %s,"
                    " please remove it or select another one"                    
                ) % ml.lot_id.name)
            ml.quantity = available_qty
