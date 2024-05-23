# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (https://www.gnu.org/licenses/agpl-3.0.html)

from odoo import fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    # TODO make it stored if move selection in output plannings becomes slow
    ls_sale_disabled = fields.Boolean(
        related="sale_line_id.order_id.logistics_schedule_disabled",
        string="Sale order - logistics schedule generation disabled",
    )

    # TODO make it stored if becomes slow
    rel_sale_order_id = fields.Many2one(
        related="sale_line_id.order_id",
        string="Related Sale Order",
        help="""
        Technical field used for logistics schedule stock move view domain
        """,
    )
