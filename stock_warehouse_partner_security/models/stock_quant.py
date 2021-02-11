# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockQuant(models.Model):
    _inherit = 'stock.quant'
    
    inventory_quantity = fields.Float(
        groups='stock.group_stock_manager,stock_warehouse_partner_security.group_stock_picking_partner'
    )
    
    @api.model
    def create(self, vals):
        """
        Creation record rules are bypassed by default, and we need disabling 
        quant creation from certain locations for group_stock_picking_partner 
        group
        """
        if self._is_inventory_mode() and 'inventory_quantity' in vals \
            and self.user_has_groups(
                'stock_warehouse_partner_security.group_stock_picking_partner'
            ) and not self.user_has_groups('stock.group_stock_manager'):
            location_allowed = (
                self.env.user.property_stock_supplier and
                self.env.user.property_stock_supplier.id == \
                    vals['location_id']
            ) or (
                self.env.user.parent_id and
                self.env.user.parent_id.property_stock_supplier and
                self.env.user.parent_id.property_stock_supplier.id == \
                    vals['location_id']
            )
            if not location_allowed:
                raise ValidationError(
                    _("Location not allowed: %s") %
                        self.env["stock.location"].browse(
                            vals['location_id']
                        ).complete_name
                )
        return super().create(vals)
            
    @api.model
    def _is_inventory_mode(self):
        return super()._is_inventory_mode() or self.user_has_groups(
            'stock_warehouse_partner_security.group_stock_picking_partner'
        )
