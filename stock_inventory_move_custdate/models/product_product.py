# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0.html
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    qty_available_lot = fields.Float(
        string="Quantity For Selected Lot",
        compute="_compute_quantities",
        digits="Product Unit of Measure",
        compute_sudo=False,
        help="""
        Quantity available taking in account context lot
        """,
    )

    def _compute_quantities(self):
        super()._compute_quantities()
        products = self.filtered(lambda p: p.type != "service")
        lot_quants = products._compute_quantities_lot_dict(
            self._context.get('lot_id'),
            self._context.get('owner_id'),
            self._context.get('package_id'),
            from_date=self._context.get('from_date'),
            to_date=self._context.get('to_date'),
        )
        for product in products:
            product.qty_available_lot = lot_quants[product.id]
        (self - products).write({"qty_available_lot": 0.0})

    def _compute_quantities_lot_dict(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        ret = dict((product.id, product.qty_available) for product in self)
        if not self.env.context.get("custdate_inventory", False):
            lot_id = False
        # When lot_id is informed, we need to exclude in & out moves
        #   regarding other lots
        moves_in_res_past, moves_out_res_past = self._get_moves_res_past_other_lots(
            lot_id, owner_id, package_id, from_date=from_date, to_date=to_date
        )
        for product_id in ret.keys():
            ret[product_id] = (
                ret[product_id]
                - moves_out_res_past.get(product_id, 0.0)
                + moves_in_res_past.get(product_id, 0.0)
            )

        return ret

    def _get_moves_res_past_other_lots(self, lot_id, owner_id, package_id, from_date=False, to_date=False):
        """
        Obtains move lines in the past that don't belong to selected lot
        for the current products
        """
        if not lot_id:
            return {}, {}
        to_date = fields.Datetime.to_datetime(to_date)
        if not (to_date and to_date < fields.Datetime.now()):
            return {}, {}
        # -----------------------------------------------------------------
        # Code that unfortunately must be copied from
        #  https://github.com/odoo/odoo/blob/15.0/addons/stock/models/product.py
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations()
        dates_in_the_past = False
        domain_move_in = [('product_id', 'in', self.ids)] + domain_move_in_loc
        domain_move_out = [('product_id', 'in', self.ids)] + domain_move_out_loc
        domain_move_in += [('lot_id', '!=', lot_id)]
        domain_move_out += [('lot_id', '!=', lot_id)]
        if owner_id is not None:
            domain_move_in += [('move_id.restrict_partner_id', '=', owner_id)]
            domain_move_out += [('move_id.restrict_partner_id', '=', owner_id)]
        domain_move_in_done = list(domain_move_in)
        domain_move_out_done = list(domain_move_out)
        if from_date:
            date_date_expected_domain_from = [('date', '>=', from_date)]
            domain_move_in += date_date_expected_domain_from
            domain_move_out += date_date_expected_domain_from
        if to_date:
            date_date_expected_domain_to = [('date', '<=', to_date)]
            domain_move_in += date_date_expected_domain_to
            domain_move_out += date_date_expected_domain_to        
        MoveLine = self.env["stock.move.line"].with_context(active_test=False)
        # Calculate the moves that were done before now to calculate back in time (as most questions will be recent ones)
        domain_move_in_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_in_done
        domain_move_out_done = [('state', '=', 'done'), ('date', '>', to_date)] + domain_move_out_done
        moves_in_res_past = dict((item['product_id'][0], item['qty_done']) for item in MoveLine.read_group(domain_move_in_done, ['product_id', 'qty_done'], ['product_id'], orderby='id'))
        moves_out_res_past = dict((item['product_id'][0], item['qty_done']) for item in MoveLine.read_group(domain_move_out_done, ['product_id', 'qty_done'], ['product_id'], orderby='id'))
        # -----------------------------------------------------------------
        return moves_in_res_past, moves_out_res_past
