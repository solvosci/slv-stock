# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, api, fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    button_exchange_lot_sn_invisible = fields.Boolean(
        compute="_compute_button_exchange_lot_sn_invisible",
    )

    def _compute_button_exchange_lot_sn_invisible(self):
        invisible_slm_ids = self.filtered(
            lambda x: not (
                x.state in ["assigned", "confirmed", "partially_available"]
                and x.product_id.tracking == "serial"
                and x.move_id.sn_should_be_readonly()
            )
        )
        invisible_slm_ids.update({"button_exchange_lot_sn_invisible": True})
        (self - invisible_slm_ids).update({"button_exchange_lot_sn_invisible": False})

    def button_exchange_lot_sn(self):
        self.ensure_one()
        Wizard = self.env["stock.move.line.exchange.sn.wizard"]
        new = Wizard.create({
            "stock_move_line_id": self.id,
        })
        return {
            "name": _("Exchange S/N Wizard"),
            'res_model': "stock.move.line.exchange.sn.wizard",
            "view_mode": "form",
            "view_type": "form",
            "res_id": new.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }
    
    def button_add_unit_lot_sn(self):
        self.ensure_one()
        self.qty_done = 1.0

    def button_remove_lot_sn(self):
        self.ensure_one()
        self.unlink()

    def _get_document(self):
        self.ensure_one()
        return (
            self.picking_id
            or False
        )
    
    @api.model
    def _get_reserved_for_sn(self, lot_id):
        # If should be one or none, because is a S/N
        return self.search([
            ("lot_id", "=", lot_id.id),
            ("state", "not in", ["done", "cancel"]),
            ("product_uom_qty", ">", 0.0),
        ])

