# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    ls_po_create_disable_default = fields.Boolean(
        string="Disable PO plannings creation by default",
        default=False,
        help="""
        When checked, a PO created with this picking operation
        won't create logistics plannings by default.
        That could be changed for any PO anyway
        """,
    )
