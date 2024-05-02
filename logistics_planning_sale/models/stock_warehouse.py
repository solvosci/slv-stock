# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models


class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"

    ls_so_create_disable_default = fields.Boolean(
        string="Disable SO plannings creation by default",
        default=False,
        help="""
        When checked, a SO created with destination this warehouse
        won't create logistics plannings by default.
        That could be changed for any SO anyway
        """,
    )
