# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def print_stock_picking_80mm(self):
        self.ensure_one()
        paper_format = self.env.ref("stock_picking_report_80mm.stock_picking_ticket")
        items = self.move_line_ids_without_package
        if len(items) > 1:
            paper_format.page_height = 85 + (len(items) * 10)
        return self.env.ref("stock_picking_report_80mm.action_stock_picking_pdf").report_action(self)
