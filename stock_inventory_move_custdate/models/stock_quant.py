# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.tools.float_utils import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    current_inventory_id = fields.Many2one(
        comodel_name="stock.inventory",
        readonly=True,
    )
    quantity_at_date = fields.Float(
        digits="Product Unit of Measure",
        compute="_compute_quantity_at_date",
        store=True,
    )

    @api.depends("current_inventory_id.date", "quantity")
    def _compute_quantity_at_date(self):
        # inventory_ids = self.env["stock.inventory"].search([
        #     ("stock_quant_ids", "in", self.ids),
        #     ("state", "=", "in_progress"),
        # ])
        quants_inventory_date = self.filtered(lambda x: x.current_inventory_id)
        for quant in quants_inventory_date:
            extra_context = {
                "custdate_inventory": True,
                "compute_child": False,
                "location": quant.location_id.id,
            }
            inventory_id = quant.current_inventory_id
            extra_context["to_date"] = inventory_id.date
            if quant.lot_id:
                extra_context["lot_id"] = quant.lot_id.id
            product_id = quant.product_id.with_context(**extra_context)
            quant.quantity_at_date = product_id.qty_available_lot
        for quant in (self - quants_inventory_date):
            quant.quantity_at_date = quant.quantity

    @api.depends("quantity_at_date")
    def _compute_inventory_diff_quantity(self):
        for quant in self:
            quant.inventory_diff_quantity = quant.inventory_quantity - quant.quantity_at_date

    @api.depends("quantity_at_date")
    def _compute_is_outdated(self):
        """
        Outdated recalculation only if is an inventory at date scenario
        (determined because quantity_date differs from quantity)
        TODO alternative code: checking current_inventory_id != False
        """
        super()._compute_is_outdated()
        for quant in self.filtered(
            lambda x: float_compare(
                x.quantity_at_date,
                x.quantity,
                precision_rounding=x.product_uom_id.rounding
            )
        ):
            if quant.product_id and float_compare(quant.inventory_quantity - quant.inventory_diff_quantity, quant.quantity_at_date, precision_rounding=quant.product_uom_id.rounding) and quant.inventory_quantity_set:
                quant.is_outdated = True
            else:
                quant.is_outdated = False

    def _apply_inventory(self):
        """
        Procedure:
        - (1) Obtain every stock inventory in progress involved in current quants
        - (2) Identify those quants that are not involved in stock inventories,
        -     or belong to a stock inventory but are actually marked as done
        -     => quants_not_in_invs => directly apply default behavior
        - (3) For those quants not in (2)-set, call _apply_inventory with the 
        -     inventory date they belong to 
        """
        quants_in_invs = self.filtered(lambda x: x.current_inventory_id and x.to_do)
        inv_ids = quants_in_invs.mapped("current_inventory_id")
        for inv in inv_ids:
            quants_inv = (
                quants_in_invs.filtered(lambda x: x.current_inventory_id == inv)
            ).with_context(
                stock_move_custom_date=inv.date
            )
            super(StockQuant, quants_inv)._apply_inventory()
        super(StockQuant, self - quants_in_invs)._apply_inventory()
