# © 2022 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

import logging

from odoo import api, models

logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        """
        Initial stuff when a move is done:
        * Internal moves: SVLs are basically created with minimum data
          and scheduled_date is prepared for custom create date (for moves and SVLs)
        * Incoming (from purchases) moves are prepared for custom create date
          (for moves and custom create date) FOR TESTING PURPOSES
        """
        done_moves = self.browse()

        # ********************************************************************
        # Internal transfers
        internal_moves = self.filtered(
            lambda x: x.picking_code == "internal"
            and x.product_id.warehouse_valuation
        )
        # Internal transfers custom date management
        # TODO we temporary use picking schedule_date
        # TODO update stuff
        # Thanks to this, move will be updated to custom date,
        #  but still not its SVLs
        if internal_moves and not self.env.context.get(
            "stock_move_custom_date", False
        ):
            # TODO assuming one picking (this could be not possible)
            stock_move_custom_date = internal_moves.mapped(
                "picking_id"
            ).scheduled_date
            internal_moves = internal_moves.with_context(
                stock_move_custom_date=stock_move_custom_date
            )

        for move in internal_moves:
            # Internal SVLs stuff, only if there's a warehouse movement
            origin = move.picking_id.location_id.get_warehouse()
            destination = move.picking_id.location_dest_id.get_warehouse()
            if origin != destination and move.quantity_done > 0.0:
                # Since internal move could be at date, we retrieve the proper price
                # TODO remove sudo() when well defined security access
                unit_cost = self.env[
                    "product.history.average.price"
                ].sudo().get_price(
                    move.product_id,
                    origin,
                    dt=internal_moves.env.context["stock_move_custom_date"]
                )

                SVL = internal_moves.env['stock.valuation.layer'].sudo()
                SVL.create({
                    'product_id': move.product_id.id,
                    'value': 0.0,
                    'unit_cost': unit_cost,
                    'quantity': -move.quantity_done,
                    'stock_move_id': move.id,
                    'warehouse_id': origin.id,
                    'company_id': self.env.user.company_id.id,
                    'description': ('%s - %s') % (move.reference, move.name)
                })
                SVL.create({
                    'product_id': move.product_id.id,
                    'value': 0.0,
                    'unit_cost': unit_cost,
                    'quantity': move.quantity_done,
                    'stock_move_id': move.id,
                    'warehouse_id': destination.id,
                    'company_id': self.env.user.company_id.id,
                    'description': ('%s - %s') % (move.reference, move.name)
                })
        done_moves |= super(StockMove, internal_moves)._action_done(
            cancel_backorder=cancel_backorder
        )
        # ********************************************************************

        # ********************************************************************
        # Incoming (and not outgoing returns)
        incoming_moves = self.filtered(
            lambda x: x.picking_code == "incoming"
            and not x.origin_returned_move_id
        )
        if incoming_moves:
            # It's possible to have different pickings            
            # TODO There's a custom date for TESTING purpose commented code
            #  that justifies processing each picking separately.
            # Without this code incoming moves could be processed together
            pickings = incoming_moves.mapped("picking_id")
            for pick in pickings:
                # in_moves = incoming_moves.filtered(
                #     lambda x: x.picking_id.id == pick.id
                # ).with_context(
                #     stock_move_custom_date=pick.scheduled_date
                # )
                in_moves = incoming_moves.filtered(
                    lambda x: x.picking_id.id == pick.id
                )
                done_moves |= super(StockMove, in_moves)._action_done(
                    cancel_backorder=cancel_backorder
                )
        # ********************************************************************

        # ********************************************************************
        # Outgoing that comes from incoming return => use incoming returned
        #  date
        outgoing_moves = self.filtered(
            lambda x: x.picking_code == "outgoing"
            and x.origin_returned_move_id
        )
        if outgoing_moves:
            # It's possible to have different pickings (but stranger)
            pickings = outgoing_moves.mapped("picking_id")
            for pick in pickings:
                out_moves = outgoing_moves.filtered(
                    lambda x: x.picking_id.id == pick.id
                )
                # We're in a single picking, so first move is enough
                #  for getting this information
                out_date = out_moves[0].origin_returned_move_id.date
                out_moves = out_moves.with_context(
                    stock_move_custom_date=out_date
                )
                done_moves |= super(StockMove, out_moves)._action_done(
                    cancel_backorder=cancel_backorder
                )
        # ********************************************************************

        # super() call for other moves, which don't suffer any changes
        done_moves |= super(
            StockMove,
            self - internal_moves - incoming_moves - outgoing_moves
        )._action_done(
            cancel_backorder=cancel_backorder
        )

        # At this point
        # * Moves SVLs are linked to their proper History Average Prices
        # * But History Average Prices could be inconsistent, due to a 
        #   recent change in the middle of the "history" (e.g. a past day)
        # So we recalculate every History entry after the oldest altered one
        done_moves._compute_phaps_and_update_slvs()

        return done_moves

    def _compute_phaps_and_update_slvs(self, phaps=False):
        phaps_processed = self.env["product.history.average.price"]
        """
        For a set of moves, makes a complete cycle
          compute PHAP older and later
          update dependendent SVLs
        """
        logger.info(
            "_compute_phaps_and_update_slvs: called for the following"
            " moves (%d): %s"
            % (len(self), self.ids)
        )
        if not phaps:
            phaps = self.sudo().stock_valuation_layer_ids.mapped(
                "history_average_price_id"
            )
        logger.info(
            "_compute_phaps_and_update_slvs: %d initial affected PHAP(s)"
            % len(phaps)
        )
        # FIXME this could cause an infinite loop!!!!!
        while phaps:
            oldest_phap = phaps.sorted(lambda x: x.date)[0]
            # TODO very conservative later PHAP election:
            #      the oldest one for every product and warehouse affected
            #      Maybe a more efficient and reduced set could be matched
            products = phaps.mapped("product_id").ids
            warehouses = phaps.mapped("warehouse_id").ids
            later_phaps = self.env[
                "product.history.average.price"
            ].sudo().search([
                ('product_id', 'in', products),
                ('warehouse_id', 'in', warehouses),
                ('date', '>=', oldest_phap.date),
            ])
            later_phaps._compute_average_price()
            # Average prices have changed for some dates, dependent
            #  valuations must change too (e.g. sale moves, internal moves)
            # In the case of internal moves, new PHAP changes should be
            #  pending, that are returned
            phaps = later_phaps._update_dependent_svls()
            # Infinite loop prevention
            phaps_processed |= later_phaps
            phaps -= phaps_processed
            logger.info(
                "_compute_phaps_and_update_slvs: %d PHAP(s) processed"
                " and %d recalculated and pending"
                % (len(phaps_processed), len(phaps))
            )

        logger.info("_compute_phaps_and_update_slvs: process finished!")

    # TODO computed field?
    def get_phap_id(self):
        """
        Obtains PHAP linked to this move
        """
        self.ensure_one()
        svls = self.stock_valuation_layer_ids
        if svls:
            phaps = svls.mapped("history_average_price_id")
            return (len(phaps) == 1) and phaps.id or False
        else:
            return False

    @api.model
    def _init_phaps(self):
        """
        Initialize PHAPs firing computation from initial purchase & transfer
        inputs and inventory adjustments for every (product, warehouse),
        based on initial valued SVLs
        EXECUTE AS SUPERUSER
        DO NOT USE BUT ON ADDON STARTUP
        """

        # *********************************************************************
        # ************************** PURCHASES ********************************
        sql_initial_purchases = """
            select
                slv2.stock_move_id smid, V.*
            from (
                select
                    svl.product_id, svl.warehouse_id, min(svl.create_date) min_date
                from
                    stock_valuation_layer svl
                inner join
                    stock_move sm on sm.id=svl.stock_move_id
                where
                    sm.state='done' and
                    sm.purchase_line_id is not null
                group by
                    svl.product_id, svl.warehouse_id
                order by
                    min_date
            ) V
            inner join
                stock_valuation_layer slv2 on
                    slv2.product_id=V.product_id and
                    slv2.warehouse_id=V.warehouse_id and
                    slv2.create_date=V.min_date
            order by
                V.min_date
            """
        self.env.cr.execute(sql_initial_purchases)
        init_psm_ids = []
        for row in self.env.cr.dictfetchall():
            init_psm_ids.append(row["smid"])

        logger.info(
            "_init_phaps: running _compute_phaps_and_update_slvs()"
            " for %d initial purchases..."
            % len(init_psm_ids)
        )
        self.browse(init_psm_ids)._compute_phaps_and_update_slvs()
        logger.info(
            "_init_phaps: finished _compute_phaps_and_update_slvs()"
            " for initial purchases!"
        )
        # *********************************************************************

        # *********************************************************************
        # ************************** TRANSFERS ********************************
        sql_initial_transfers = """
            select
                slv2.stock_move_id smid, V.*
            from (
                select
                    svl.product_id, svl.warehouse_id, min(svl.create_date) min_date 
                from
                    stock_valuation_layer svl
                inner join
                    stock_move sm on sm.id=svl.stock_move_id
                inner join
                    stock_picking sp on sp.id=sm.picking_id
                inner join
                    stock_picking_type spt on spt.id=sp.picking_type_id
                where
                    sm.state='done' and
                    spt.code='internal' and
                    svl.quantity > 0
                group by
                    svl.product_id, svl.warehouse_id
                order by
                    min_date
            ) V
            inner join
                stock_valuation_layer slv2 on
                    slv2.product_id=V.product_id and
                    slv2.warehouse_id=V.warehouse_id and
                    slv2.create_date=V.min_date
            order by
                V.min_date
            """
        self.env.cr.execute(sql_initial_transfers)
        init_tsm_ids = []
        for row in self.env.cr.dictfetchall():
            init_tsm_ids.append(row["smid"])

        logger.info(
            "_init_phaps: running _compute_phaps_and_update_slvs()"
            " for %d initial transfers..."
            % len(init_tsm_ids)
        )
        self.browse(init_tsm_ids)._compute_phaps_and_update_slvs()
        logger.info(
            "_init_phaps: finished _compute_phaps_and_update_slvs()"
            " for initial transfers!"
        )
        # *********************************************************************

        # *********************************************************************
        # ******************** INVENTORY ADJUSTMENTS **************************
        sql_initial_inv_adj = """
            select
                slv2.stock_move_id smid, V.*
            from (
                select
                    svl.product_id, svl.warehouse_id, min(svl.create_date) min_date 
                from
                    stock_valuation_layer svl
                inner join
                    stock_move sm on sm.id=svl.stock_move_id
                inner join
                    stock_location slo on slo.id=sm.location_id
                inner join
                    stock_location sld on sld.id=sm.location_dest_id
                where
                    sm.state='done' and
                    sm.picking_id is null and
                    (slo.usage='inventory' or sld.usage='inventory')
                group by
                    svl.product_id, svl.warehouse_id
                order by
                    min_date
            ) V
            inner join
                stock_valuation_layer slv2 on
                    slv2.product_id=V.product_id and
                    slv2.warehouse_id=V.warehouse_id and
                    slv2.create_date=V.min_date
            order by
                V.min_date
            """
        self.env.cr.execute(sql_initial_inv_adj)
        init_ism_ids = []
        for row in self.env.cr.dictfetchall():
            init_ism_ids.append(row["smid"])

        logger.info(
            "_init_phaps: running _compute_phaps_and_update_slvs()"
            " for %d initial inventory adjustments..."
            % len(init_ism_ids)
        )
        self.browse(init_ism_ids)._compute_phaps_and_update_slvs()
        logger.info(
            "_init_phaps: finished _compute_phaps_and_update_slvs()"
            " for initial inventory adjustments!"
        )
        # *********************************************************************
