# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class MoveWeight(models.TransientModel):
    _name = 'stock.move.weight.wizard'

    name = fields.Char('Description')
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env.company,
                                 index=True,
                                 required=True)
    picking_id = fields.Many2one('stock.picking')
    picking_classification_ids = fields.One2many(related="picking_id.picking_classification_ids")
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        related="picking_id.partner_id",
    )

    move_line_weight_ids = fields.One2many(
        comodel_name='stock.move.line.weight.wizard',
        inverse_name='move_weight_id')

    move_id = fields.Many2one('stock.move')

    weight_selection = fields.Selection([
        ('theoretical_qty', _('Announced Qty')),
        ('net_weight', _('Scale Weight'))],
        default='net_weight')

    theoretical_qty = fields.Float(
        string='Announced Qty',
        digits='Product Unit of Measure')
    net_weight = fields.Float(
        string='Net',
        digits='Product Unit of Measure')

    weight_selected = fields.Float(
        digits='Product Unit of Measure',
        compute='_compute_weight_selected')
    weight_classified = fields.Float(
        digits='Product Unit of Measure',
        compute='_compute_weight_classified',
        string='Weight Pending Classification ',
        readonly=True,
        store=True)

    product_id = fields.Many2one(
        'product.product',
        related="move_id.product_id")

    note = fields.Text(
        string='Notes',
        related="picking_id.note")
    internal_note = fields.Text(string='Internal Notes')

    check_move_line_ids = fields.Boolean()
    purchase_order_id = fields.Many2one("purchase.order")
    vehicle_id = fields.Many2one("vehicle.vehicle")

    @api.onchange('weight_selection')
    @api.depends('weight_selected')
    def _compute_weight_selected(self):
        if self.weight_selection == 'theoretical_qty':
            self.weight_selected = self.theoretical_qty
        else:
            self.weight_selected = self.net_weight

    @api.depends('move_line_weight_ids.product_uom_qty', 'weight_selected')
    def _compute_weight_classified(self):
        self.weight_classified = self.weight_selected - sum(self.move_line_weight_ids.mapped('product_uom_qty'))
        if self.weight_classified == self.weight_selected:
            self.check_move_line_ids = True
        else:
            self.check_move_line_ids = False

    def move_weight_autofill_difference(self):
        self.ensure_one()
        product_qty = self.move_line_weight_ids[-1].product_uom_qty
        self.move_line_weight_ids[-1].update({
            'product_uom_qty': product_qty + self.weight_classified
        })
        return self.move_id._move_weight_open_wizard(self.id)

    def move_weight_autofill(self):
        self.ensure_one()
        self.move_line_weight_ids = [(0, 0, {
            'product_id': self.product_id.id,
            'product_uom_qty': self.weight_selected
        })]

        # Workaround: reopen wizard
        # See (solution #1):
        # https://stackoverflow.com/questions/31963214/odoo-prevent-button-from-closing-wizard/31971881#31971881
        return self.move_id._move_weight_open_wizard(self.id)

    def purchase_order_new(self):
        """ This function should be overidden if other addons
            add new purchase data
        """
        purchase_order = self.env['purchase.order']
        order_new = purchase_order.new({
            'partner_id': self.partner_id.id
        })
        order_new.onchange_partner_id()
        order_new.onchange_partner_user_id()

        # TODO stock_picking_mgmt_weight_pp: future addon to link with purchase_pricelist
        # order_new.onchange_partner()
        return order_new

    def purchase_order_line_update_prices(self, pol):
        pol._product_id_change()
        pol._onchange_quantity()
        # purchase_pricelist_slv new onchange method
        pol.product_id_change()

        # TODO stock_picking_mgmt_weight_pp: future addon to link with purchase_pricelist
        # pol.product_id_change()
        # pol.product_uom_change()

        if pol.related_real_order_line_id:
            pol.price_unit = (
                pol.related_real_order_line_id.price_unit
            )
            pol.discount = (
                pol.related_real_order_line_id.discount
            )

    def purchase_order_get_origin(self):
        origin_orders = self.move_line_weight_ids.mapped(
            "order_line_id.order_id"
        )
        return (
            origin_orders and ", ".join(origin_orders.mapped("name"))
            or False
        )

    def write_operations(self):
        """
        Starts classification operations.
        In this first step, some initial validations are performed, and a new
        purchase order is created if no one is selected.
        Then, validation() continues process
        """
        self.ensure_one()
        # TODO ¿float_is_zero?        
        if self.weight_classified > 0:
            raise ValidationError(_("Weight pending classification must be zero"))

        purchase_order = self.env['purchase.order']
        order_new = self.purchase_order_new()
        order_new.origin = self.purchase_order_get_origin()
        purchase_order |= purchase_order.create(
            order_new._convert_to_write(order_new._cache)
        )
        purchase_order.write({"date_order": self.move_id.date})
        self.validation(purchase_order)

        """
        if self.weight_classified == 0:
            # if not self.move_line_weight_ids.mapped('order_line_id'):
            #     order_new = self.purchase_order_new()
            #     purchase_order |= purchase_order.create(
            #         order_new._convert_to_write(order_new._cache))
            #     self.validation(purchase_order, False)

            # elif len(self.move_line_weight_ids.mapped('order_line_id')) == 1:
            #     for record in self.move_line_weight_ids.filtered(lambda x: x.order_line_id.id != False):
            #         purchase_order = record.order_line_id.order_id
            #         break
            #     self.validation(purchase_order, True)
            if len(self.move_line_weight_ids.mapped('order_line_id')) <= 1:
                order_new = self.purchase_order_new()
                purchase_order |= purchase_order.create(
                    order_new._convert_to_write(order_new._cache))

                origin_order = False
                for record in self.move_line_weight_ids.filtered(lambda x: x.order_line_id.id != False):
                    origin_order = record.order_line_id.order_id
                    break
                # if self.move_line_weight_ids.filtered(lambda x: x.order_line_id.id != False):
                #     origin_order = self.move_line_weight_ids.filtered(lambda x: x.order_line_id.id != False).order_line_id.order_id

                self.validation(purchase_order, origin_order)                
            else:
                raise ValidationError(_("There should only be a single purchase order"))
        else:
            raise ValidationError(_("Weight pending classification must be zero"))
        """

    def validation(self, purchase_order):
        """
        Finishes classification process:
        - Adds classification operation as order lines, taking in care price calculation
        - Marks those lines as fully done (qty_done) in the newly created picking.
        - Remove demanded quantities for purchase classification lines
        - Links classification and related scale picking
        - Cancels scale classificated picking
        - Partly validates classification picking, in order to effectively
        receive classificated quantities
        - Process the remaining picking generated, reflecting actual pending
        quantities, and removing their empty lines, or even the full picking,
        if the whole order is processed
        """
        pol_initial = purchase_order.order_line

        for move_line in self.move_line_weight_ids:
            if move_line.order_line_id:
                related_real_order_line_id = move_line.order_line_id.id
            else:
                related_real_order_line_id = False

            purchase_order.order_line = [(0, 0, {
                'name': move_line.product_id.name,
                'product_id': move_line.product_id.id,
                'product_qty': move_line.product_uom_qty,
                'product_uom': move_line.product_uom_id.id,
                'price_unit': 0.0,
                'date_planned': purchase_order.date_order,
                'related_real_order_line_id': related_real_order_line_id,
                'qty_classified': move_line.product_uom_qty,
                'classified': True,
                'discount': 0.0,
            })]
            self.picking_id.picking_classification_ids = [(0, 0, {
                "order_line_id": move_line.order_line_id and move_line.order_line_id.id or False,
                "picking_id": self.picking_id.id,
                "product_id": move_line.product_id.id,
                "product_qty": move_line.product_uom_qty,
                "clasification_date": fields.datetime.now(),
                "user_id": self.env.user.id,
                "weight_selection": self.weight_selection,
            })]

        pol_new = purchase_order.order_line - pol_initial
        for new_order_line in pol_new:
            # Set proper unit price by seller, or apply the related line one
            # new_order_line._product_id_change()
            # new_order_line._onchange_quantity()
            # if new_order_line.related_real_order_line_id:
            #     new_order_line.price_unit = (
            #         new_order_line.related_real_order_line_id.price_unit
            #     )
            #     new_order_line.discount = (
            #         new_order_line.related_real_order_line_id.discount
            #     )
            self.purchase_order_line_update_prices(new_order_line)

        self.picking_id.write({
            "classification_purchase_order_id": purchase_order.id
        })

        pol_new.order_id.write({
            'internal_note': self.internal_note,
        })

        # for move in classification_picking.move_ids_without_package.filtered(lambda x: x.purchase_line_id.classified):
        #     move.move_line_ids.write({
        #         'qty_done': move.purchase_line_id.product_qty
        #     })

        # for order_line in purchase_order.order_line.filtered(
        #     lambda x: x.classified and x.qty_received == 0
        # ):
        #     order_line.write({
        #         'product_qty': 0
        #     })

        # classification_picking.write({
        #     "related_picking_id": self.picking_id.id
        # })
        # self.picking_id.write({
        #     "classification_picking_id": classification_picking.id
        # })

        self.picking_id.action_cancel()
        # classification_picking.button_validate()

    def update_operations(self):
        """
        When lines are updated only one line should have a linked purchase line
        """
        if not self.env.user.has_group("stock_picking_mgmt_weight.group_sc_manager"):
            user_ids = self.picking_id.picking_classification_ids.user_id.ids
            if self.env.user.id not in user_ids:
                raise ValidationError(_(
                    "Classification modification not allowed for you"
                ))
        for pol in self.move_line_weight_ids.filtered(
            lambda x: x.old_order_line_id != x.order_line_id
        ):
            pol.classification_order_line_id.write({
                "related_real_order_line_id": pol.order_line_id.id,
            })
            self.purchase_order_line_update_prices(
                pol.classification_order_line_id
            )
            # TODO Computed data update workaround
            # Remove it when classification_order_line_ids is actually stored
            (pol.order_line_id + pol.old_order_line_id)._compute_pending_qty()

        # TODO maybe this operation should be optional,
        # if no changes are detected
        # TODO make function for this (is repeated from validation method)
        # origin_orders = self.move_line_weight_ids.mapped(
        #     "order_line_id.order_id"
        # )
        # # self.purchase_order_id.related_order_ids = [(6, 0, origin_orders.ids)]
        # self.purchase_order_id.origin = (
        #     origin_orders and ", ".join(origin_orders.mapped("name"))
        #     or False
        # )
        self.purchase_order_id.origin = self.purchase_order_get_origin()
        """
        pol = self.move_line_weight_ids.filtered(lambda x: x.order_line_id)
        if len(pol) != 1:
            raise ValidationError(_("There should only be a purchase order"))
        if pol.old_order_line_id != pol.order_line_id.id:
            pol.classification_order_line_id.write({
                "related_real_order_line_id": pol.order_line_id.id,
            })
            self.purchase_order_line_update_prices(
                pol.classification_order_line_id
            )
            # Manual related order update
            new_purchase_order_id = pol.order_line_id.order_id
            if new_purchase_order_id != self.purchase_order_id:
                self.purchase_order_id.write({
                    "related_order_id": pol.order_line_id.order_id.id,
                    "origin": pol.order_line_id.order_id.name,
                })
            # TODO Computed data update workaround
            # Remove it when classification_order_line_ids is actually stored
            (pol.order_line_id + pol.old_order_line_id)._compute_pending_qty()
        """
        # if len(self.move_line_weight_ids.mapped('order_line_id')) == 1 :      
        #     for move_line in self.move_line_weight_ids:
        #         for order_line in self.purchase_order_id.order_line.filtered(lambda x: x.product_id == move_line.product_id and x.related_real_order_line_id is not False):
        #             if move_line.order_line_id:
        #                 order_line.write({
        #                     'related_real_order_line_id': move_line.order_line_id.id
        #                 })
        #                 break
        #     self.purchase_order_id.write({
        #         "related_order_id": self.move_line_weight_ids.filtered(lambda x: x.order_line_id).order_line_id.order_id.id
        #     })
        #     self.picking_id.write({
        #         'classification_purchase_order_id': self.purchase_order_id.id
        #     })
        # else:
        #     raise ValidationError(_("There should only be a purchase order"))
