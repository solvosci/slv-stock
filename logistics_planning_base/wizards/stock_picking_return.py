# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    def create_returns(self):
        if not self.env.context.get("skip_ask_return", False):
            wiz_new = self.env["stock.return.picking.ls.wizard"].create({
                "stock_return_picking_id": self.id,
            })
            return {
                "name": _("Confirm Schedules creation"),
                "res_model": "stock.return.picking.ls.wizard",
                "view_mode": "form",
                "view_type": "form",
                "res_id": wiz_new.id,
                "target": "new",
                "type": "ir.actions.act_window",
            }
        return super().create_returns()

    def _create_returns(self):
        new_picking_id, picking_type_id = super()._create_returns()
        if self.env.context.get("create_ls", False):
            ls_values, to_ready = self.env["stock.picking"].browse(
                new_picking_id
            )._get_prepared_ls_returns()
            if ls_values:
                ls_ids = self.env["logistics.schedule"].sudo().create(ls_values)
                if to_ready:
                    ls_ids._action_ready()
        
        return new_picking_id, picking_type_id
