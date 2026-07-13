# © 2025 Solvos Consultoría Informática (http://www.solvos.es)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _action_confirm(self, merge=True, merge_into=False):
        if self.env.context.get('from_sale_order'):
            merge = False
        return super()._action_confirm(merge=merge, merge_into=merge_into)
