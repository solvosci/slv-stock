# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import _, api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    button_add_sn_invisible = fields.Boolean(
        compute="_compute_button_add_sn_invisible",
    )
    move_line_ids_readonly = fields.Boolean(
        compute="_compute_move_line_ids_readonly",
    )

    @api.depends("state", "product_id.tracking", "picking_type_id.code")
    def _compute_button_add_sn_invisible(self):
        for move in self:
            move.button_add_sn_invisible = (
                move.product_id.tracking != "serial"
                or move.state in ["cancel", "done"]
                or not move.sn_should_be_readonly()
            )

    @api.depends("state", "is_locked", "product_id.tracking", "picking_type_id.code")
    def _compute_move_line_ids_readonly(self):
        """
        Original attrs in form view:
        attrs="{'readonly': ['|', ('state', '=', 'cancel'), '&amp;', ('state', '=', 'done'), ('is_locked', '=', True)]}"
        We only add OR for S/N products in an outgoing move
        """        
        for move in self:
            move.move_line_ids_readonly = (
                move.state == "cancel"
                or (move.state == "done" and move.is_locked)
                or (
                    move.product_id.tracking == "serial"
                    and move.sn_should_be_readonly()
                )
            )

    def sn_should_be_readonly(self):
        self.ensure_one()
        return (
            self.picking_type_id
            and self.picking_type_id.code == "outgoing"
            or False
        )

    def button_add_sn(self):
        self.ensure_one()
        Wizard = self.env["stock.move.line.add.sn.wizard"]
        new = Wizard.create({
            "stock_move_id": self.id,
        })
        return {
            "name": _("Add S/N Wizard"),
            'res_model': "stock.move.line.add.sn.wizard",
            "view_mode": "form",
            "view_type": "form",
            "res_id": new.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }
