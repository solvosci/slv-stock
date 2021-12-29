# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, _, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    shipping_resource_id = fields.Many2one(
        comodel_name="shipping.resource",
        default=lambda self: self.env["shipping.resource"].get_default(),
    )

    # TODO remove field
    related_order_id = fields.Many2one(
        comodel_name="purchase.order",
        readonly=True,
    )
    related_order_ids = fields.Many2many(
        string="Related orders",
        comodel_name="purchase.order",
        relation="purchase_order_related",
        column1="order_id",
        column2="related_order_id",
        compute="_compute_related_order_ids",
        store=True,
    )
    related_order_count = fields.Integer(
        compute="_compute_related_order_ids",
        store=True,
        readonly=False,
    )

    classification_order_ids = fields.Many2many(
        string="Related orders",
        comodel_name="purchase.order",
        relation="purchase_order_related",
        column1="related_order_id",
        column2="order_id",
    )
    classification = fields.Boolean(
        compute="_compute_classification",
        store=True,
        readonly=True,
        help="Shows if the order comes from a classification",
    )
    classification_count = fields.Integer(
        compute="_compute_classification_count"
    )
    cancelled_classif_count = fields.Integer(
        compute="_compute_classification_count"
    )

    classification_date = fields.Datetime(
        compute="_compute_classification_date",
    )

    has_pending_qty = fields.Boolean(
        compute="_compute_has_pending_qty",
        help="Instrumental field indicating if there's any pending quantity"
        " for this order",
    )

    classification_stock_picking_ids = fields.Many2many(
        comodel_name="stock.picking",
        compute="_compute_classification_stock_picking_ids"
    )
    scale_stock_move_ids = fields.Many2many(
        comodel_name="stock.move",
        compute="_compute_scale_stock_move_ids"
    )
    scale_stock_move_count = fields.Integer(
        compute="_compute_scale_stock_move_count"
    )

    invoice_orig_pend = fields.Monetary(
        string="Pend. invoicing (original)",
        store=True,
        readonly=True,
        compute="_compute_invoice_orig_pend",
        help="Total amount currently pending of invoice (original)",
    )
    invoice_pend = fields.Monetary(
        string="Pend. invoicing",
        store=True,
        readonly=True,
        compute="_compute_invoice_pend",
        help="Total amount currently pending of invoice",
    )
    receive_pend = fields.Monetary(
        string="Pend. receiving",
        store=True,
        readonly=True,
        compute="_compute_receive_pend",
        help="Total amount currently pending of receive",
    )
    invoice_status_ext = fields.Selection(
        [
            ('no', 'Nothing to Bill (recv. pend.)'),
            ('to invoice', 'Waiting Bills'),
            ('to invoice classif', 'Waiting Bills (classif.)'),
            ('invoiced', 'Fully Billed'),
        ],
        string='Billing Status (Extended)',
        compute='_compute_invoice_status_ext',
        store=True,
        readonly=True,
        copy=False,
        default='no',
    )

    classification_invoice_ids = fields.Many2many(
        compute="_compute_classification_invoice_ids"
    )
    classification_invoice_count = fields.Integer(
        compute="_compute_classification_invoice_ids"
    )

    def _compute_classification_invoice_ids(self):
        for record in self:
            lines = record.classification_order_ids.invoice_ids.invoice_line_ids.filtered(
                lambda x: x.purchase_line_id.related_real_order_id.id == record.id
            )
            if lines:
                record.classification_invoice_ids = [(4, invoice.id)
                                                     for invoice in lines.move_id]
            else:
                record.classification_invoice_ids = False

            record.classification_invoice_count = \
                len(record.classification_invoice_ids)

    @api.depends("order_line.related_real_order_line_id")
    def _compute_related_order_ids(self):
        for record in self:
            record.related_order_ids = [(
                6,
                0,
                record.order_line.mapped(
                    "related_real_order_line_id.order_id"
                ).ids
            )]
            record.related_order_count = len(record.related_order_ids)

    # def _compute_new_related_order_ids(self):
    #     for record in self:
    #         record.new_related_order_ids = record.order_line.filtered(lambda x: x.related_real_order_line_id is not False).related_real_order_line_id.order_id.ids

    # def _compute_classification_order_ids(self):
    #     for record in self:
    #         record.classification_order_ids = record.search([('new_related_order_ids', '=', record.id)]).ids

    @api.depends("order_line.classified")
    def _compute_classification(self):
        for record in self:
            record.classification = (
                len(record.order_line.filtered("classified")) > 0
            )

    def _compute_classification_count(self):
        for record in self:
            record.classification_count = len(record.classification_order_ids)
            # It should be 0 or 1, or even more if quantities are incremented
            record.cancelled_classif_count = len(
                record.classification_order_ids.filtered(
                    lambda x: x.state == "cancel"
                )
            )

    def _compute_classification_date(self):
        StockPickingClassification = self.env["stock.picking.classification"]
        for record in self:
            if record.classification:
                classification_ids = StockPickingClassification.search([
                    ("picking_id.classification_purchase_order_id", "=", record.id),
                ])
                record.classification_date = (
                    classification_ids
                    and classification_ids[0].clasification_date
                    or False
                )
            else:
                record.classification_date = False

    def _compute_has_pending_qty(self):
        for record in self:
            # TODO float_is_zero
            record.has_pending_qty = (
                sum(record.order_line.mapped("pending_qty")) > 0
            )

    def _compute_classification_stock_picking_ids(self):
        for record in self:
            record.classification_stock_picking_ids = (
                self.env['stock.picking'].search([('classification_purchase_order_id', 'in', record.classification_order_ids.ids)])
            )
            # record.classification_stock_picking_ids = (
            #     self.env['stock.picking'].search([('origin_purchase_order_id', '=', record.id)])
            # )

    def _compute_scale_stock_move_ids(self):
        for record in self:
            record.scale_stock_move_ids = record.classification_stock_picking_ids.move_lines

    def _compute_scale_stock_move_count(self):
        for record in self:
            record.scale_stock_move_count = len(record.scale_stock_move_ids)

    @api.depends(
        "order_line.qty_received",
        "order_line.qty_invoiced",
        "order_line.price_unit_wd",
    )
    def _compute_invoice_orig_pend(self):
        # TODO make line.qty_invoiced_pend field and use here?
        for record in self:
            record.invoice_orig_pend = sum([
                max(line.qty_received - line.qty_invoiced, 0) * line.price_unit_wd
                for line in record.order_line
            ])

    @api.depends("order_line.qty_invoiced_pend", "order_line.price_unit_wd")
    def _compute_invoice_pend(self):
        for record in self:
            record.invoice_pend = sum([
                line.qty_invoiced_pend * line.price_unit_wd
                for line in record.order_line
            ])

    @api.depends("order_line.pending_qty", "order_line.price_unit_wd")
    def _compute_receive_pend(self):
        for record in self:
            record.receive_pend = sum([
                line.pending_qty * line.price_unit_wd
                for line in record.order_line
            ])

    @api.depends("state", "invoice_orig_pend", "invoice_pend", "receive_pend")
    def _compute_invoice_status_ext(self):
        # TODO float_compare, float_is_zero
        for record in self:
            if record.state not in ("purchase", "done"):
                record.invoice_status_ext = "no"
            elif record.invoice_orig_pend > 0:
                record.invoice_status_ext = "to invoice"
            elif record.invoice_orig_pend == 0.0 and record.invoice_pend > 0:
                record.invoice_status_ext = "to invoice classif"
            elif record.invoice_pend == 0.0 and record.receive_pend > 0:
                record.invoice_status_ext = "no"
            else:
                record.invoice_status_ext = "invoiced"

    @api.onchange('partner_id')
    def onchange_partner(self):
        pass
        # TODO stock_picking_mgmt_weight_pp: future addon to link with purchase_pricelist
        # super().onchange_partner()
        # if not self.partner_id.purchase_pricelist_id:
        #     values = {
        #         'pricelist_id': self.env.ref('stock_picking_mgmt_weight.purchase_pricelist_default').id,
        #     }
        # self.update(values)

    def action_classification_orders(self):
        action = self.env.ref("purchase.purchase_rfq").read()[0]
        action['context'] = self.env.context
        action['domain'] = [('related_order_ids', 'in', self.id)]
        return action

    def action_scale_stock_moves(self):
        # TODO make our own action, since original is deeply changed here
        action = self.env.ref(
            "stock_picking_mgmt_weight.stock_move_weights_historical"
        ).read()[0]
        action['context'] = self.env.context
        action["view_mode"] = "tree"
        action["views"] = [
            (self.env.ref(
                "stock_picking_mgmt_weight"
                ".stock_move_mgmt_weight_frontend_weight_tree_view_readonly"
                ).id, "tree"),
        ]
        action['domain'] = [('origin_purchase_order_id', '=', self.id)]
        return action

    def action_update_related_order_id(self):
        # TODO merge with stock.move.move_weight()
        self.ensure_one()
        picking_id = self.env['stock.picking'].search([('classification_purchase_order_id', '=', self.id)])
        Wizard = self.env['stock.move.weight.wizard']
        move_id = picking_id.move_ids_without_package

        if move_id.net_weight == sum(self.order_line.mapped('product_uom_qty')):
            weight_selection = 'net_weight'
        else:
            weight_selection = 'theoretical_qty'

        new = Wizard.create({
            'move_id': move_id.id,
            'weight_selection': weight_selection,
            'theoretical_qty': move_id.theoretical_qty,
            'net_weight': move_id.net_weight,
            'picking_id': picking_id.id,
            'company_id': picking_id.company_id.id,
            'purchase_order_id': self.id,
            'move_line_weight_ids': [(0, 0, {
                'classification_order_line_id': line.id,
                'order_line_id': line.related_real_order_line_id.id,
                'old_order_line_id': line.related_real_order_line_id.id,
                'product_id': line.product_id.id,
                'product_uom_qty': line.product_uom_qty
                }) for line in self.order_line]
        })

        return {
            'name': _('Move Weight'),
            'res_model': 'stock.move.weight.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref(
                "stock_picking_mgmt_weight.view_stock_move_weight_wizard_inherit_form_weight"
            ).id,
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'stock_move_line_weight': True}
        }

    def action_view_classification(self):
        self.ensure_one()
        picking_id = self.env['stock.picking'].search([('classification_purchase_order_id', '=', self.id)])
        return picking_id.move_ids_without_package.action_view_classification()

    def action_related_orders(self):
        action = self.env.ref("purchase.purchase_form_action").read()[0]
        action['context'] = self.env.context
        action['domain'] = [('classification_order_ids', 'in', self.id)]
        return action

    def action_cancel_pending(self):
        """
        Finishes selected orders, cancelling pending quantities.
        For achieve it, an instrumental cancelled classification order is
        created
        """
        if self.classification:
            raise UserError(_(
                "Cannot cancel pending quantities for %s:"
                " it's a classification order"
            ) % self.name)
        if self.state not in ("purchase", "done"):
            raise UserError(_(
                "Cannot cancel pending quantities for %s:"
                " it's not an order yet"
            ) % self.name)
        if not self.classification_count:
            raise UserError(_(
                "Cannot cancel pending quantities for %s:"
                " it's not an order made of classification orders"
            ) % self.name)
        if not self.has_pending_qty:
            raise UserError(_(
                "Cannot cancel pending quantities for %s:"
                " nothing is pending"
            ) % self.name)

        order_new = self._action_cancel_pending_create()
        po_cancel = self.env['purchase.order'].create(
            order_new._convert_to_write(order_new._cache)
        )
        for line in self.order_line.filtered(
            lambda x: x.pending_qty > 0
        ):
            po_cancel.order_line = [(0, 0, {
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_qty': line.pending_qty,
                'product_uom': line.product_uom.id,
                'price_unit': line.price_unit,
                'date_planned': fields.datetime.now(),
                'related_real_order_line_id': line.id,
                'qty_classified': 0.0,
                # TODO classified is needed here to mark the whole order
                'classified': True,
                'discount': 0.0,
            })]
        po_cancel.button_cancel()

    def action_cancel_pending_multi(self):
        for record in self.browse(self.env.context["active_ids"]):
            record.action_cancel_pending()

    def _action_cancel_pending_create(self):
        """
        This method should be overridden by other addons
        """
        order_new = self.env['purchase.order'].new({
            "partner_id": self.partner_id.id
        })
        order_new.onchange_partner_id()
        order_new.origin = self.name
        order_new.internal_note = _(
            "Created when cancelling pending quantities of %s"
        ) % self.name
        return order_new

    def action_classification_invoice(self):
        action = self.env.ref("account.action_move_in_invoice_type").read()[0]
        action['context'] = self.env.context
        action['domain'] = [('id', 'in', self.classification_invoice_ids.ids)]
        return action

    def action_view_invoice(self):
        result = super().action_view_invoice()
        # TODO Datetime to Date (according timezone)
        pt_base_date = False
        # if self.classification:
        #     pt_base_date = self.date_order
        # else:
        #     done_pickings = self.picking_ids.filtered(
        #         lambda x: x.state == "done"
        #     ).sorted(key="date_done")
        #     pt_base_date = (
        #         done_pickings and done_pickings[-1].date_done or False
        #     )
        # if pt_base_date:
        #     result["context"]["default_invoice_pt_base_date"] = pt_base_date
        # TODO default base date unset by default
        result["context"]["default_invoice_pt_base_date"] = pt_base_date

        return result
