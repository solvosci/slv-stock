# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, _


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    def action_open_assigned_wizard(self):
        Wizard = self.env['sp.assigned.wizard']
        new = Wizard.create({
            'picking_type_id': self.id
        })

        return {
            'name': _('Assign sale order'),
            'res_model': 'sp.assigned.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }
