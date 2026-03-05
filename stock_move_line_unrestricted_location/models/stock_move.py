# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)
from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"

    warehouse_view_location_dest_id = fields.Many2one(
        "stock.location",
        string="Warehouse view destination location",
        related="location_dest_id.warehouse_id.view_location_id",
        store=True
    )

    warehouse_view_location_src_id = fields.Many2one(
        "stock.location",
        string="Warehouse view source location",
        related="location_id.warehouse_id.view_location_id",
        store=True
    )
