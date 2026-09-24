# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (http://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _action_generate_immediate_wizard(self, show_transfers=False):
        if self.filtered(lambda x: x.picking_type_code == 'outgoing'):
            raise ValidationError(
                _("Picking cannot be validated if there is no quantity done.")
            )

        return super()._action_generate_immediate_wizard(
            show_transfers=show_transfers
        )
