# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields

class StockQuantDraftWiz(models.TransientModel):
    _name = "stock.quant.draft.warn.wiz"
    _description = "Stock Quant Draft Warn Wizard"

    stock_inventory_id = fields.Many2one(comodel_name="stock.inventory", required=True)
    product_ids = fields.Many2many('product.product', string="Involved products (10 max)", readonly=True)
    warning_message = fields.Char(readonly=True)

    def button_continue(self):
        return self.stock_inventory_id.with_context(stock_inventory_check_set_quants=False).action_view_inventory_adjustment()
