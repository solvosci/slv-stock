# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo import _, fields, models, api
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class ProductHistoryAveragePrice(models.Model):
    _name = "product.history.average.price"
    _inherit = ["mail.thread"]
    _description = "Product Average Price by Warehouse and Date"

    svl_ids = fields.One2many('stock.valuation.layer', 'history_average_price_id')
    product_average_price_id = fields.Many2one('product.average.price')

    date = fields.Date()
    product_id = fields.Many2one('product.product')
    warehouse_id = fields.Many2one('stock.warehouse')

    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', 'Currency', related='company_id.currency_id', readonly=True, required=True)

    average_price_edit = fields.Monetary(
        compute="_compute_average_price_edit",
        inverse="_inverse_average_price_edit",
        string="New average price",
        help="Technical field that allow us to edit averagre price",
    )
    average_price = fields.Monetary(
        compute="_compute_average_price",
        store=True,
        tracking=True,
        help="Average price for this product and warehouse at this date",
    )
    average_price_manual = fields.Boolean(
        readonly=True,
        tracking=True,
        help="Shows if last average price was manually set",
    )
    average_price_manual_dt = fields.Datetime(
        readonly=True,
        help="When price was manually set, shows the change date",
    )
    average_price_manual_user = fields.Many2one(
        comodel_name="res.users",
        readonly=True,
        help="When price was manually set, shows the user that made this change",
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

    def _compute_average_price_edit(self):
        for phap in self:
            phap.average_price_edit = phap.average_price

    def _inverse_average_price_edit(self):
        # This method should actually be called as sudo()
        self.ensure_one()
        # TODO float_compare
        if self.average_price_edit < 0.0:
            raise ValidationError(_("Average price cannot be negative!"))
        self.write({
            "average_price": self.average_price_edit,
            "stock_valuation": self.stock_quantity * self.average_price_edit,
            "average_price_manual": True,
            "average_price_manual_dt": fields.Datetime.now(),
            "average_price_manual_user": self.env.user.id,
        })
        # Now we need to update subsequent PHAPs but this one. Otherwise
        #  its average price should be re-calculated and lost
        self.svl_ids.stock_move_id._compute_phaps_and_update_slvs(
            phap_omit=self
        )

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
        # Audit manual values should be unset, because this method is only
        #  fired when normal update process is fired
        self.filtered(lambda x: x.average_price_manual).write({
            "average_price_manual": False,
            "average_price_manual_dt": False,
            "average_price_manual_user": False,
        })

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

    def button_price_edit(self):
        self.ensure_one()
        Wizard = self.env["phap.price.edit.wizard"]
        new = Wizard.create({
            "phap_id": self.id,
            "average_price_new": self.average_price,
        })
        return {
            "name": _("Average Price Edit Wizard"),
            'res_model': "phap.price.edit.wizard",
            "view_mode": "form",
            "view_type": "form",
            "res_id": new.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }

    def button_qty_edit(self):
        self.ensure_one()
        Wizard = self.env["phap.qty.edit.wizard"]
        new = Wizard.create({
            "phap_id": self.id,
            "stock_quantity_new": self.stock_quantity,
        })
        return {
            "name": _("Quantity Edit Wizard"),
            'res_model': "phap.qty.edit.wizard",
            "view_mode": "form",
            "view_type": "form",
            "res_id": new.id,
            "target": "new",
            "type": "ir.actions.act_window",
        }

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

    def _update_quantity(self, location_id, stock_quantity_new):
        """
        Updates this PHAP stock quantity, applying it to a certain location.
        """
        self.ensure_one()
        # TODO no lots & packages, but we should ensure on it
        quant_obj = self.env["stock.quant"]
        quant = quant_obj.search([
            ("product_id", "=", self.product_id.id),
            ("location_id", "=", location_id.id),
        ])
        # FIXME it works with UTC+x countries, e.g.
        #       for CET we'll obtain mm/dd/yyyy 01:00:00,
        #       Improve it when possible
        stock_move_custom_date = self.date
        # Workaround: in stock.quantity the available quantity is
        #  the quantity _today_.
        # So we have to hack current process quantity making _today_
        #  the equivalent quantity adjustment
        # e.g
        # - At 01/10/2023 we've got 15 and we want to update to 25.
        #   So we want to increase 10.
        # - But today there are 6.
        # - Then, we should "update" quantity to 16 = 6 + (25-15),
        #   with the proper date in context
        quant_diff = stock_quantity_new - self.stock_quantity
        if quant:
            quantity_adj = quant.quantity + quant_diff
            quant.with_context(
                inventory_mode=True,
                stock_move_custom_date=stock_move_custom_date
            ).inventory_quantity = quantity_adj
        else:
            # It's supposed to call create method in this case, because
            #  _today_ has no stock quant entries yet
            quant_obj.with_context(
                inventory_mode=True,
                stock_move_custom_date=stock_move_custom_date
            ).create({
                "product_id": self.product_id.id,
                "location_id": location_id.id,
                "inventory_quantity": quant_diff,
            })
