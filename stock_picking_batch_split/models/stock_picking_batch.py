# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, _


class StockPickingBatch(models.Model):
    _inherit="stock.picking.batch"

    def action_open_stock_picking_batch_split_wizard(self):
        Wizard = self.env["stock.picking.batch.split.wizard"]
        new = Wizard.create({
            'batch_id': self.id
        })
        return{
            "name": _("Split Picking By Product"),
            'view_mode': 'form',
            "res_model": "stock.picking.batch.split.wizard",
            "type":"ir.actions.act_window",
            "target":"new",
            "res_id":new.id,
        }
