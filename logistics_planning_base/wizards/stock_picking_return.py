# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def _create_returns(self):    
        new_picking_id, picking_type_id = super()._create_returns()
        ls_values, to_ready = self.env["stock.picking"].browse(
            new_picking_id
        )._get_prepared_ls_returns()
        if ls_values:
            ls_ids = self.env["logistics.schedule"].sudo().create(ls_values)
            if to_ready:
                ls_ids._action_ready()
        
        return new_picking_id, picking_type_id
