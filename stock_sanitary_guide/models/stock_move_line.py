# Copyright 2026 Solvos Consultoría Informática, S.L. (<https://www.solvos.es>)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    sanitary_guide_id = fields.Many2one(
        "sanitary.guide",
        string="Sanitary Guide",
        help="Sanitary guide (Documento de orixe) this line's lot came in "
            "with.",
    )

    def action_open_sanitary_guide_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Sanitary Guide",
            "res_model": "sanitary.guide.lookup.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_move_line_id": self.id,
                "default_guide_number": self.sanitary_guide_id.guide_number,
            },
        }
