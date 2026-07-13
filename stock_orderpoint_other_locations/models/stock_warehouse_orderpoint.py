# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    other_location_ids = fields.Many2many(
        comodel_name="stock.location",
        string="Other Locations",
        compute="_compute_other_location_ids",
        store=True,
        readonly=False,
        check_company=True,
        help="""
        When set, locations filled are taken in account when calculating
        available and virtual quantities, during procurement rules execution.
        Then, obtained quantities for these locations are added to available
        stock count and should prevent firing rules
        """,
    )

    @api.depends("warehouse_id")
    def _compute_other_location_ids(self):
        # Prevent other locations located in a wrong warehouse
        for orderpoint in self.filtered(lambda x: x.other_location_ids):
            if (
                orderpoint.warehouse_id.id
                not in
                orderpoint.other_location_ids.warehouse_id.ids
            ):
                orderpoint.other_location_ids = False

    def _get_product_context(self):
        # Take in account this new locations when obtaning available and
        # virtual quantities when determining qty_to_order for the rule
        ret = super()._get_product_context()
        if self.other_location_ids:
            ret["location"] = self.other_location_ids.ids + (
                isinstance(ret["location"], list)
                and ret["location"]
                or [ret["location"]]
            )
        return ret
    
    @api.depends("other_location_ids")
    def _compute_qty(self):
        # Enables qty_to_order recompute when other locations are added
        super()._compute_qty()
