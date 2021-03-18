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
    def _get_custom_locations(self):
        my_location_ids = []
        if self.env.user.property_stock_supplier:
            my_location_ids.append(
                self.env.user.property_stock_supplier.id
            )
        if self.env.user.parent_id and \
            self.env.user.parent_id.property_stock_supplier:
            my_location_ids.append(
                self.env.user.parent_id.property_stock_supplier.id
            )            
        return my_location_ids

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
            if not vals['location_id'] in self._get_custom_locations():
                raise ValidationError(
                    _("Location not allowed: %s") %
                        self.env["stock.location"].browse(
                            vals['location_id']
                        ).complete_name
                )
        return super().create(vals)
            
    @api.model
    def _is_inventory_mode(self):
        return super()._is_inventory_mode() or (
            self.env.context.get('inventory_mode') is True 
            and self.user_has_groups(
                'stock_warehouse_partner_security.group_stock_picking_partner'
            )
        )

    @api.model
    def _get_quants_action(self, domain=None, extend=False):
        if self.env.context.get("show_my_inventory", False):
            my_location_ids = self._get_custom_locations()
            # Prevent accessing to every location when no locations were 
            # defined for this user
            if len(my_location_ids) == 0:
                my_location_ids.append(0)

            my_domain = [("location_id", "in", my_location_ids)]
            domain = (domain and domain + my_domain) or my_domain

        return super()._get_quants_action(domain=domain, extend=extend)
