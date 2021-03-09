# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class Picking(models.Model):
    _inherit = "stock.picking"

    @api.depends('move_lines.move_orig_ids.state')
    def _compute_state(self):
        result = super()._compute_state()
        # the picking state also depends of the origin movements state
        for pick in self:
            if pick.state == 'assigned':
                pick.state = pick.move_lines._get_state_among_origin_moves()
