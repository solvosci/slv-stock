# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import api, fields, models, api
import pdb


class StockValuationLayer(models.Model):
    _inherit = "stock.valuation.layer"

    create_date_valuation = fields.Datetime(
        default=lambda self: fields.Datetime.now(),
        readonly=True,
    )
    warehouse_id = fields.Many2one('stock.warehouse')
    average_price = fields.Monetary(string="Average price on creation")

    history_average_price_id = fields.Many2one('product.history.average.price')

    accumulated = fields.Boolean()
    is_return = fields.Boolean(default=False)

    document_origin = fields.Char()
    move_reference = fields.Char(
        related="stock_move_id.reference",
        store=True,
    )

    warehouse_valuation = fields.Boolean(
        related="product_id.warehouse_valuation",
    )

    origin_type = fields.Selection(
        selection=[
            ("purchase", "Purchase"),
            ("sale", "Sale"),
            ("internal", "Internal"),
            ("adjustment", "Adjustment"),
            ("scrap", "Scrap"),
        ],
        compute="_compute_origin_type",
        store=True,
        string="Type",
        help="""
        Possible types:
        - purchase - comes from a purchase or purchase return
        - sale - comes from a sale or sale return
        - internal - internal transfer
        - adjustment - Inventory adjustment
        - scrap - Scrap
        """,
    )
    origin_partner_id = fields.Many2one(
        related="stock_move_id.picking_partner_id",
        string="Partner",
    )

    @api.model
    def create(self, vals):
        if vals.get("stock_move_id"):
            picking_types = ['incoming', 'outgoing', 'internal']
            product_id = self.env['product.product'].browse(vals.get("product_id"))
            move_id = self.env["stock.move"].browse(vals["stock_move_id"])
            locations = (move_id.location_id + move_id.location_dest_id)
            inv_location = locations.filtered(lambda x: x.usage == "inventory")

            # For custom warehouse valuation products, only picking-based
            #  moves and inventory adjustments will be processed
            if (
                product_id.categ_id.warehouse_valuation
                and
                (
                    (move_id.picking_id and move_id.picking_code in picking_types)
                    or len(inv_location) > 0
                )
            ):
                if not vals.get("warehouse_id"):
                    if move_id.picking_id:
                        # FIXME this is wrong: for a certain picking from/to location could be manually changed
                        vals["warehouse_id"] = move_id.picking_type_id.warehouse_id.id
                    else:
                        # Inventory adjustment
                        vals["warehouse_id"] = (
                            locations - inv_location
                        ).get_warehouse().id

                vals["accumulated"] = False
                vals["document_origin"] = (
                    inv_location and move_id.name
                    or
                    move_id.picking_id.origin
                )

                # Actual Date determination
                # For now, to possible sources
                # * Internal transfers, within this module, see stock_move.py
                # * Any other module that injects the related context value
                date = self.env.context.get(
                    "stock_move_custom_date",
                    False
                ) or fields.Datetime.now()
                # date = move_id.picking_id.scheduled_date
                # if not move_id.picking_id:
                #     date = fields.Datetime.now()

                quantity = move_id.quantity_done

                history_last_day, history_today = self.get_history_values(vals.get("product_id"), vals.get("warehouse_id"), date)

                average_price_last = history_last_day.average_price
                if history_today:
                    average_price_last = history_today.average_price

                if move_id.picking_type_id.code == 'incoming':
                    # TODO include incomings not linked with sales nor purchases!!
                    # Purchase order (original or "2*N return")
                    # if not move_id.origin_returned_move_id:
                    if move_id.purchase_line_id:
                        # vals["unit_cost"] = move_id.price_unit
                        vals["unit_cost"] = move_id.purchase_line_id.price_unit
                        vals["value"] = vals.get("unit_cost") * vals.get("quantity")
                        vals["accumulated"] = True
                    # Sale return "2*N + 1"
                    else:
                        # orig_move = move_id.origin_returned_move_id
                        # FIXME Wrong!!! This should be the same price unit of
                        #  sale move valuation, not order line
                        # Anyway, this will recalculated later (in 
                        #  phap._update_dependent_svls ??)
                        # vals["unit_cost"] = orig_move.sale_line_id.price_unit
                        vals["unit_cost"] = move_id.sale_line_id.price_unit
                        vals["value"] = vals.get("unit_cost") * vals.get("quantity")
                        # TODO this should be return always a value,
                        #  but False is possible!!!
                        # vals["history_average_price_id"] = orig_move.get_phap_id()
                        vals["history_average_price_id"] = (
                            move_id.origin_returned_move_id.stock_valuation_layer_ids.history_average_price_id.id
                        )

                elif move_id.picking_type_id.code == 'outgoing':
                    # Sale order (original or "2*N return")
                    # TODO remove it? It should be later recalculated
                    # if not move_id.origin_returned_move_id:
                    if move_id.sale_line_id:
                        vals["unit_cost"] = move_id.product_id.standard_price_warehouse_ids.filtered(lambda x: x.warehouse_id.id == move_id.picking_type_id.warehouse_id.id).average_price
                        vals["value"] = vals.get("unit_cost") * vals.get("quantity")
                    # Purchase return "2*N + 1"
                    else:
                        # orig_move = move_id.origin_returned_move_id
                        # vals["unit_cost"] = orig_move.price_unit
                        vals["unit_cost"] = move_id.purchase_line_id.price_unit
                        quantity = -quantity
                        vals["value"] = vals.get("unit_cost") * quantity
                        vals["accumulated"] = True
                        # TODO this should be return always a value,
                        #  but False is possible!!!
                        # vals["history_average_price_id"] = orig_move.get_phap_id()
                        vals["history_average_price_id"] = (
                            move_id.origin_returned_move_id.stock_valuation_layer_ids.history_average_price_id.id
                        )

                elif move_id.picking_type_id.code == 'internal':
                    vals["value"] = vals.get("unit_cost") * vals.get("quantity")
                    if vals.get("quantity") > 0:
                        vals["accumulated"] = True

                elif inv_location:
                    # Inventory adjustment
                    vals["unit_cost"] = self.env[
                        "product.history.average.price"
                    ].sudo().get_price(
                        move_id.product_id,
                        self.env["stock.warehouse"].browse(
                            vals["warehouse_id"]
                        ),
                        dt=date
                    )
                    vals["value"] = vals.get("unit_cost") * vals.get("quantity")

                if vals.get("accumulated"):
                    # TODO we protect this code, but this "average_price"
                    #      should be removed, since is unused
                    if (history_last_day.total_quantity + history_today.total_quantity_day + quantity) > 0.0:
                        vals["average_price"] = (history_last_day.total_quantity * history_last_day.average_price + (history_today.summary_entry + vals.get("value"))) / (history_last_day.total_quantity + history_today.total_quantity_day + quantity)
                    else:
                        vals["average_price"] = 0.0
                else:
                    if average_price_last > 0:
                        vals["average_price"] = average_price_last
                    else:
                        vals["average_price"] = history_last_day.average_price

                # FIXME special SVL moves (like returns) should be linked
                #  to original PHAP related move. If get_phap_id() does not
                #  locate  it, this if will be the "default" value
                if not vals.get("history_average_price_id", False):
                    vals["history_average_price_id"] = self.product_history_link(vals.get("product_id"), vals.get("warehouse_id"), vals.get("average_price"), vals.get("quantity"), vals.get("value"), vals.get("accumulated"), history_today, date)

        # TODO update date by cr call, is it needed?
        return super(StockValuationLayer, self).create(vals)

    @api.depends("stock_move_id")
    def _compute_origin_type(self):
        for svl in self:
            origin_type = False
            sm = svl.stock_move_id
            if sm.purchase_line_id:
                origin_type = "purchase"
            elif sm.sale_line_id:
                origin_type = "sale"
            elif sm.scrapped:
                origin_type = "scrap"
            elif sm.picking_type_id.code == "internal":
                origin_type = "internal"
            elif (sm.location_id | sm.location_dest_id).filtered(
                lambda x: x.usage == "inventory"
            ):
                origin_type = "adjustment"
            svl.origin_type = origin_type

    def get_history_values(self, product_id, warehouse_id, date):
        PHAP = self.env['product.history.average.price'].sudo()
        history_last_day = PHAP.search([
            ('product_id', '=',  product_id),
            ('warehouse_id', '=', warehouse_id),
            ('date', '<', date)],
            order="date desc", limit=1)
        history_today = PHAP.search([
            ('product_id', '=',  product_id),
            ('warehouse_id', '=', warehouse_id),
            ('date', '=', date)
        ])
        return history_last_day, history_today

    def product_history_link(self, product_id, warehouse_id, average_price, quantity, value, accumulated, history_today, date):
        PAP = self.env['product.average.price'].sudo()
        PHAP = self.env['product.history.average.price'].sudo()
        price_warehouse = PAP.search([
            ('product_id', '=', product_id),
            ('warehouse_id', '=', warehouse_id)
        ])
        if not price_warehouse:
            price_warehouse = PAP.create({
                'product_id': product_id,
                'warehouse_id': warehouse_id,
                'average_price': average_price,
            })

        if history_today:
            history_average = history_today
        else:
            history_average = PHAP.create({
                'date': date.date(),
                'product_id': product_id,
                'warehouse_id': warehouse_id,
                'average_price': average_price,
                'total_quantity_day': quantity,
                'total_quantity': quantity,
                'product_average_price_id': price_warehouse.id
            })

        if accumulated:
            not_accumulated = self.search([
                ('accumulated', '=', False),
                ('history_average_price_id', '=', history_average.id)
            ])
            for record in not_accumulated:
                record.unit_cost = average_price
                record.value = record.unit_cost * record.quantity

            # TODO replace with PHAP.search?
            # subsequent_records = self.history_average_price_id.search([
            # subsequent_records = PHAP.search([
            #     ('product_id', '=',  product_id),
            #     ('warehouse_id', '=', warehouse_id),
            #     ('date', '>', date.date())
            # ])
            # if subsequent_records:
            #     subsequent_records.recalculation_average_price(quantity, average_price, value, history_average)

        return history_average.id
