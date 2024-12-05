# © 2025 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html
from odoo import fields, models


class SNLockedMixin(models.AbstractModel):
    _name = "sn.locked.mixin"
    _description = "S/N Locked Mixin"

    sn_locked = fields.Boolean(
        string="S/N Locked",
        copy=False,
        tracking=True,
        help="Indicates if S/Ns are locked for this document",
    )
    sn_locked_invisible = fields.Boolean(
        string="S/N Locked is invisible",
        compute="_compute_sn_locked_invisible",
    )

    def _compute_sn_locked_invisible(self):
        self.update({"sn_locked_invisible": False})
