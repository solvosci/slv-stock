# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import models, fields


class StockPicking(models.Model):
    _inherit = "stock.picking"

    change_picking_type_enabled = fields.Boolean(
        compute="_change_picking_type_enabled",
        string="Is Picking Operation Change Enabled",
        help=
        """
        Technical field indicating whether 
        """,
    )

    def _change_picking_type_enabled(self):
        available_states = self.env[
            "stock.move.change.source.location.wizard"
        ]._get_allowed_states()
        allowed_picks = self.filtered(
            lambda x: x.state in available_states and x.picking_type_code == "outgoing"
        )
        allowed_picks.write({"change_picking_type_enabled": True})
        (self - allowed_picks).write({"change_picking_type_enabled": False})
