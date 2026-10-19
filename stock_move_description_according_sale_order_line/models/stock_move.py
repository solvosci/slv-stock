# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model_create_multi
    def create(self, vals_list):
        ret = super().create(vals_list)
        for move in ret:
            move._set_description_picking()
        return ret

    def _set_description_picking(self):
        self.ensure_one()
        if self.sale_line_id:
            self.description_picking = self.sale_line_id.name
