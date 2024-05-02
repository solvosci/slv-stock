# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"    

    def stock_move_split_picking(self):
        wizard_id = self.env['stock.split.picking'].create({
            'mode': 'selection',
            'picking_ids': [(4, self.picking_id.id)],
            'move_ids': [(4, self.id)]
        })
        wizard_id.action_apply()
