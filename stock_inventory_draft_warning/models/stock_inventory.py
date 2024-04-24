# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, models, api


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    def action_view_inventory_adjustment(self):
        if self.env.context.get("stock_inventory_check_set_quants", True):
            products_with_diff_quantity = self.stock_quant_ids.filtered(lambda x: x.inventory_quantity_set)
            if products_with_diff_quantity:
                return self.action_open_stock_quant_draft_warn_wiz(products_with_diff_quantity)
        result = super(StockInventory, self).action_view_inventory_adjustment()
        return result
    
    def action_open_stock_quant_draft_warn_wiz(self, products_with_diff_quantity):
        
        limited_products = products_with_diff_quantity[:10]

        wizard = self.env['stock.quant.draft.warn.wiz'].create({
            "stock_inventory_id": self.id,
            "warning_message": _("There are %d pending inventory adjustments. Please complete them first") % len(products_with_diff_quantity),
            "product_ids": limited_products.mapped("product_id").ids,
        })
        return {
            'name': _('Pending Inventory Adjustments'),
            'res_model': 'stock.quant.draft.warn.wiz',
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': wizard.id,
            "context": {},
        }
