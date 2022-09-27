# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo import _, fields, models, api

logger = logging.getLogger(__name__)


class ProductHistoryAveragePrice(models.Model):
    _name = "product.history.average.price"
    _description = "Product Average Price by Warehouse and Date"

    svl_ids = fields.One2many('stock.valuation.layer', 'history_average_price_id')
    product_average_price_id = fields.Many2one('product.average.price')

    date = fields.Date()
    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('stock.warehouse')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True, required=True)
    average_price = fields.Monetary(
        compute="_compute_average_price",
        store=True,
        help="Average price for this product and warehouse at this date",
    )

    total_quantity_day = fields.Float(
        string="Total inputs",
        compute="_compute_average_price",
        store=True,
        help="Shows the total quantity of this day and warehouse in inputs "
        "that modify average price computation (e.g. purchases, internal "
        "incoming transfers)"
    )
    total_quantity = fields.Float(
        string="Total accum. inputs",
        compute="_compute_average_price",
        store=True,
    )
    summary_entry = fields.Float(
        compute="_compute_average_price",
        store=True,
        help="Techical field for Total Inputs valuation",
    )

    stock_quantity = fields.Float(
        compute="_compute_average_price",
        store=True,
        help="Stock for this product and warehouse at this date",
    )
    stock_valuation = fields.Monetary(
        compute="_compute_average_price",
        help="Stock valuation for this product and warehouse at this date",
        store=True,
    )

    def name_get(self):
        # TODO better date formatting, depending on language context
        # TODO display_name instead of name_get()?
        return [
            (
                phap.id,
                _("%s in %s at %s")
                %
                (phap.product_id.display_name, phap.warehouse_id.name, phap.date),
            )
            for phap in self
        ]

    @api.depends("svl_ids")
    def _compute_average_price(self):
        phap_count = len(self)
        phap_index = 0
        for record in self.sorted(lambda x: x.date):
            phap_index += 1
            logger.info(
                "_compute_average_price: called for %s (%d/%d)..."
                % (record.display_name, phap_index, phap_count)
            )
            # if record.svl_ids.filtered(lambda x: x.accumulated is True).sorted(key=lambda r: r.create_date, reverse=True):
            #     record.average_price = record.svl_ids.filtered(
            #         lambda x: x.accumulated is True).sorted(key=lambda r: r.create_date_valuation, reverse=True)[0].average_price
            # else:
            #     record.average_price = 0

            record.total_quantity_day = sum(record.svl_ids.filtered(
                lambda x: x.accumulated is True).mapped('quantity'))

            # FIXME Why not total_quantity_day + total_quantity of the previous record??
            # record.total_quantity = record.total_quantity_day + sum(self.search([
            #     ('product_id', '=', record.product_id.id),
            #     ('warehouse_id', '=', record.warehouse_id.id),
            #     ('date', '<', record.date)]).mapped('total_quantity_day'))
            phap_prev = self.search([
                ('product_id', '=', record.product_id.id),
                ('warehouse_id', '=', record.warehouse_id.id),
                ('date', '<', record.date)], order="date desc", limit=1)
            record.total_quantity = record.total_quantity_day + (phap_prev and phap_prev.total_quantity or 0.0)

            record.summary_entry = sum(record.svl_ids.filtered(
                lambda x: x.accumulated is True).mapped('value'))

            # AVERAGE PRICE UPDATE - old code based on "total_quantity_day"
            # if phap_prev and (record.total_quantity_day + phap_prev.total_quantity) > 0:
            #     record.average_price = (record.summary_entry + phap_prev.total_quantity*phap_prev.average_price) / (record.total_quantity_day + phap_prev.total_quantity)
            # else:
            #     record.average_price = record.total_quantity_day and (record.summary_entry / record.total_quantity_day) or 0.0
            # AVERAGE PRICE UPDATE - based on stock_quantity
            # Case #1: last date stock quantity was positive, no matter
            #          current date stock quantity sign => standard formula
            # Case #2: last date stock quantity was negative and current date
            #          stock is also negative => average price remains the same
            # Case #3: last date stock quantity was negative and current date
            #          stock becomes positive => average price is the current
            #          date one
            if phap_prev and phap_prev.stock_quantity > 0.0:
                record.average_price = (
                    record.summary_entry
                    +
                    phap_prev.stock_quantity*phap_prev.average_price
                ) / (record.total_quantity_day + phap_prev.stock_quantity)
            elif (
                phap_prev
                and phap_prev.stock_quantity < 0.0
                and (phap_prev.stock_quantity + record.total_quantity_day) < 0.0
            ):
                record.average_price = phap_prev.average_price
            else:
                record.average_price = record.total_quantity_day and (
                    record.summary_entry / record.total_quantity_day
                ) or 0.0

            # At last, we can update current stock valuation
            # TODO warehouse filter probably unnecessary
            record.stock_quantity = (
                (phap_prev and phap_prev.stock_quantity or 0.0)
                +
                sum(
                    record.svl_ids.filtered(
                        lambda x: x.warehouse_id.id == record.warehouse_id.id
                    ).mapped("quantity")
                )
            )
            record.stock_valuation = record.stock_quantity * record.average_price

    def _update_dependent_svls(self):
        """
        For the selected PHAPs, current average price is propagated to
        dependent SVLs.
        Return PHAPs indirectly affected (e.g. related to internal
        incomings) that should fire a subsequent compute and update
        """
        return_phaps = self.browse()
        for phap in self:
            logger.info(
                "_update_dependent_svls: called for %s..."
                % phap.display_name
            )
            update_svls = self.env["stock.valuation.layer"]
            for svl in phap.svl_ids:
                # move = svl.stock_move_id
                # # Sale and sale returns
                # if move and move.sale_line_id:
                #     update_svls |= svl
                # svl.unit_cost = phap.average_price
                # svl.value = svl.unit_cost * svl.quantity
                # Internal outgoing and paired incoming
                # In this case, we also update incoming, but linked PHAP must
                #  be informed, because it must be recomputed
                # TODO float_compare for quantity comparisons?
                # if move and move.picking_code == "internal" and svl.quantity < 0.0:
                #     update_svls |= svl
                #     # This should be only one
                #     incoming_slv = move.stock_valuation_layer_ids.filtered(
                #         lambda x: x.quantity > 0.0
                #     )
                #     update_svls |= incoming_slv
                #     return_phaps |= incoming_slv.history_average_price_id
                upd_svls, ret_phaps = self._from_svl_get_upd_svls_and_ret_phaps(svl)
                update_svls |= upd_svls
                return_phaps |= ret_phaps

            for svl in update_svls:
                svl.unit_cost = phap.average_price
                svl.value = svl.unit_cost * svl.quantity

        return return_phaps

    def _from_svl_get_upd_svls_and_ret_phaps(self, svl):
        """
        From affected SVL, this function should return extra SVLs
        that should be updated and subsequent PHAP that should be
        recomputed.
        In this addon, we've got three different cases:
        * Sale and sale returns
        * Incoming and outgoing internal moves
        * Inventory adjustments

        This method could be overriden and add new cases
        """
        upd_svls = self.env["stock.valuation.layer"]
        ret_phaps = self.browse()
        # Sale and sale returns
        move = svl.stock_move_id
        if move and move.sale_line_id:
            upd_svls |= svl
        # Internal outgoing and paired incoming
        # In this case, we also update incoming, but linked PHAP must
        #  be informed, because it must be recomputed
        # TODO float_compare for quantity comparisons?
        if move and move.picking_code == "internal" and svl.quantity < 0.0:
            upd_svls |= svl
            # This should be only one
            incoming_slv = move.stock_valuation_layer_ids.filtered(
                lambda x: x.quantity > 0.0
            )
            upd_svls |= incoming_slv
            ret_phaps |= incoming_slv.history_average_price_id
        # Inventory adjustment
        if (
            move
            and
            (move.location_id + move.location_dest_id).filtered(
                lambda x: x.usage == "inventory"
            )
        ):
            upd_svls |= svl

        return upd_svls, ret_phaps

    # TODO remove as unnecessary (replaced by stkco_move.py later recalculation "in the future")
    def recalculation_average_price(self, last_quantity, last_average_price, last_value, last_day_id):
        last_day_id.total_quantity_day += last_quantity
        last_day_id.total_quantity += last_quantity
        last_day_id.average_price = last_average_price
        last_day_id.summary_entry += last_value
        last_day = last_day_id
        # for record in self.sorted(key=lambda x: x.date, reverse=True):
        for record in self.sorted(key=lambda x: x.date, reverse=False):
            # FIXME last_day actually is the previous record (see last line of for)
            # last_day = self.search([('product_id', '=', record.product_id.id), ('warehouse_id', '=', record.warehouse_id.id), ('date', '<', record.date)], order="date", limit=1)
            record.total_quantity += last_quantity
            record.average_price = (last_day.total_quantity * last_day.average_price + (record.summary_entry)) / (last_day.total_quantity + record.total_quantity_day)
            last_day = record

    @api.model
    def get_price(self, product_id, warehouse_id, dt=False):
        """
        Returns the current price for this input or 0.0, if not found
        The selected date is the closest in the past
        """
        # TODO better obtaining date in the user timezone?
        dt = (dt or fields.Datetime.now())
        history_price = self.search([
            ("product_id", "=", product_id.id),
            ("warehouse_id", "=", warehouse_id.id),
            ("date", "<=", dt),
        ], order="date desc", limit=1)
        return history_price and history_price.average_price or 0.0
