from odoo import api, fields, models


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    inventory_quantity = fields.Float(
        groups='stock.group_stock_manager,stock_warehouse_partner_security.group_stock_picking_partner'
    )
    
    location_partner_ids = fields.Many2many(
        'stock.location',
        compute="_compute_location_partner_ids", 
        groups='stock_warehouse_partner_security.group_stock_picking_partner',
    )
    

    def _compute_location_partner_ids(self):  
        for record in self:
            location_partners = self.env["stock.location"]
            if self.env.user.property_stock_supplier:
               location_partners |= self.env.user.property_stock_supplier
            if self.env.user.parent_id and self.env.user.parent_id.property_stock_supplier:
               location_partners |= self.env.user.parent_id.property_stock_supplier
            record.location_partner_ids = location_partners

            
    @api.model
    def _is_inventory_mode(self):
        return super()._is_inventory_mode() or self.user_has_groups('stock_warehouse_partner_security.group_stock_picking_partner')
