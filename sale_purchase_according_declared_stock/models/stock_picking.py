# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    def _compute_state(self):
        result = super()._compute_state()
        # redo this function from stock.picking
        for pick in self:
            if pick.state == 'assigned':
                pick.state = pick.move_lines._get_state_among_origin_moves()
