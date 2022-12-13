# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import api, models


class StockMove(models.Model):
    _inherit = "stock.move"

    @api.model
    def create(self, vals_list):
        ret = super().create(vals_list)
        for move in ret.sudo():
            move._set_description_picking()
        return ret

    def _set_description_picking(self):
        """
        If new models are involved, add here or inherit this module and
        overread this method.
        This method is called in sudo() mode
        """
        self.ensure_one()
        if "sale_line_id" in self and self["sale_line_id"]:
            self.description_picking = self["sale_line_id"].name
        elif "purchase_line_id" in self and self["purchase_line_id"]:
            self.description_picking = self["purchase_line_id"].name
