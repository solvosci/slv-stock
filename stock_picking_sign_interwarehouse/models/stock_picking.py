# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 (http://www.gnu.org/licenses/agpl-3.0.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_interwarehouse = fields.Boolean(
        string="Inter-warehouse transfer",
        compute="_compute_is_interwarehouse",
        store=True,
    )

    @api.depends('picking_type_code', 'location_id', 'location_dest_id')
    def _compute_is_interwarehouse(self):
        interwarehouse = self.filtered(
            lambda x: x.picking_type_code == "internal"
            and x.location_id.warehouse_id
            and x.location_dest_id.warehouse_id
            and x.location_id.warehouse_id != x.location_dest_id.warehouse_id
        )
        interwarehouse.is_interwarehouse = True
        (self - interwarehouse).is_interwarehouse = False
