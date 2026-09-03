# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, _


class StockLot(models.Model):
    _inherit = "stock.lot"

    def open_stock_lot_available_at_date_wizard(self):
        wizard = self.env["report.stock.lot.date.wizard"].create({
            "date": fields.Date.today()
        })
        return {
            "name": _("Lots at Date"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "report.stock.lot.date.wizard",
            "res_id": wizard.id,
            "target": "new",
        }
