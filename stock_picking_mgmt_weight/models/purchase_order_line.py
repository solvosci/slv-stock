# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, models, fields, api
from odoo.osv import expression


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    related_real_order_line_id = fields.Many2one(
        "purchase.order.line",
        help="For extra lines created in classification process, this field"
        " indicates the original linked line",
    )
    related_real_order_id = fields.Many2one(
        related="related_real_order_line_id.order_id",
        store=True,
    )
    classification_order_line_ids = fields.Many2many(
        string="Clasification order lines",
        comodel_name="purchase.order.line",
        relation="purchase_order_line_classif",
        column1="order_line_id",
        column2="classif_order_line_id",
        compute="_compute_classification_order_line_ids",
        store=True,
    )
    classified = fields.Boolean(default=False)
    pending_qty = fields.Float(
        compute='_compute_pending_qty',
        digits='Product Unit of Measure',
        store=True
    )
    qty_received_ext = fields.Float(
        compute='_compute_pending_qty',
        digits='Product Unit of Measure',
        store=True,
        string="Received (extended)",
        help="This field also takes in account received"
        " quantities in classification order lines"
    )
    qty_cancelled = fields.Float(
        compute="_compute_qty_cancelled",
        digits="Product Unit of Measure",
        store=True,
        string="Cancelled",
        help="This field only takes in account quantities"
        " in cancelled classification orders",
    )

    price_unit_wd = fields.Float(
         string="Unit Price W/discount",
         compute="_compute_price_unit_wd",
         store=True,
         readonly=False,
         help="Technical field for pending invoicing amount data",
    )

    qty_invoiced_ext = fields.Float(
        compute="_compute_qty_invoiced_ext",
        digits="Product Unit of Measure",
        store=True,
        string="Invoiced (extended)",
        help="This field also takes in account invoiced"
        " quantities in classification order lines"
    )
    qty_invoiced_pend = fields.Float(
        compute="_compute_qty_invoiced_pend",
        digits="Product Unit of Measure",
        store=True,
        string="Invoiced pending",
    )
    invoice_lines_invoice_first_date = fields.Datetime(
        compute="_compute_invoice_lines_invoice_first_date",
        string="Invoice first date",
    )

    # TODO remove this field and its compute function?
    # With new requirements is unnecessary
    product_qty_readonly = fields.Boolean(
        compute="_compute_product_qty_readonly",
    )
    qty_classified = fields.Float(
        digits='Product Unit of Measure',
        readonly=True
    )

    date_planned_search = fields.Date(
        compute="_compute_date_planned_search",
        store=True,
        readonly=True
    )

    identification_document_number = fields.Char(
        help="This code should be unique for an order and product LER code"
        " and should come from GAIA integration",
    )

    order_user_id = fields.Many2one(related="order_id.user_id")
    order_incoterm_id = fields.Many2one(related="order_id.incoterm_id")
    
    order_shipping_resource_id = fields.Many2one(related="order_id.shipping_resource_id")

    def name_get(self):
        context = self.env.context
        if context.get('stock_move_line_weight', False):
            result = []
            for pol in self:
                # TODO add order line description, when is different to product name
                name = _("%s-%s (%.2f pend.)") % (
                    pol.order_id.name, pol.product_id.name, pol.pending_qty
                )
                result.append((pol.id, name))
            return result
        else:
            return super().name_get()

    @api.model
    def _name_search(self, name, args=None, operator="ilike", limit=100, name_get_uid=None):
        """
        Custom search from classification wizard
        We only add order number search. Partner name is unnecessary,
        because lines are previously filtered by picking partner
        """
        if self.env.context.get('stock_move_line_weight', False):
            args = args or []
            domain = []
            if name:
                domain = [
                    "|",
                    ("name", operator, name),
                    ("order_id.name", operator, name),
                ]
            rec = self._search(
                expression.AND([domain, args]), limit=limit,
                access_rights_uid=name_get_uid,
            )
            product_id = self.env.context.get('product_id')
            return models.lazy_name_get(
                self.browse(rec).with_user(name_get_uid).sorted(key=lambda x: (x.product_id.id != product_id, x.date_order))
            )
        else:
            return super()._name_search(name=name, args=args, operator=operator, limit=limit, name_get_uid=name_get_uid)

    @api.depends(
        "order_id.classification_order_ids.order_line.related_real_order_line_id"
    )
    def _compute_classification_order_line_ids(self):
        for record in self:
            record.classification_order_line_ids = [(
                6,
                0,
                record.order_id.classification_order_ids.order_line.filtered(
                     lambda x: x.related_real_order_line_id.id == record.id
                ).ids
            )]
    # def _compute_classification_order_line_ids(self):
    #     for record in self:
    #         record.classification_order_line_ids = (
    #             record.order_id.classification_order_ids.order_line.filtered(
    #                 lambda x: x.related_real_order_line_id.id == record.id
    #             )
    #         )

    @api.depends(
        "classification_order_line_ids",
        "classification_order_line_ids.qty_received",
        "qty_received",
        "product_qty",
        "qty_cancelled",
    )
    def _compute_pending_qty(self):
        # TODO rename method
        """
        Computes pending and received custom quantities:
        - When an order is a standalone one, or a classification one,
          original qty_received is used, as Odoo did.
        - When an order has classification related orders, the new 
          qty_received_ext field instead uses product_qty related lines field
        - Mixing classification and direct reception is not supported and 
          results should be unexpected
        """
        for record in self:
            total_received = (
                record.qty_received +
                sum(record.classification_order_line_ids.mapped("product_qty")) -
                record.qty_cancelled
            )
            record.qty_received_ext = total_received
            record.pending_qty = max(
                record.product_qty - total_received - record.qty_cancelled,
                0
            )

    @api.depends("classification_order_line_ids.state")
    def _compute_qty_cancelled(self):
        for record in self:
            record.qty_cancelled = sum(
                record.classification_order_line_ids.filtered(
                    lambda x: x.state == "cancel"
                ).mapped("product_qty")
            )

    @api.depends("price_subtotal", "product_qty")
    def _compute_price_unit_wd(self):
        for record in self:
            # TODO float_is_zero usage
            if record.product_qty == 0.0:
                record.price_unit_wd = 0.0
            else:
                record.price_unit_wd = (
                    record.price_subtotal / record.product_qty
                )

    @api.depends(
        "qty_invoiced",
        "classification_order_line_ids",
        "classification_order_line_ids.qty_invoiced",
    )
    def _compute_qty_invoiced_ext(self):
        for record in self:
            total_invoiced = (
                record.qty_invoiced +
                sum(record.classification_order_line_ids.mapped("qty_invoiced"))
            )
            record.qty_invoiced_ext = total_invoiced

    @api.depends("qty_invoiced_ext", "qty_received_ext")
    def _compute_qty_invoiced_pend(self):
        for record in self:
            record.qty_invoiced_pend = max(
                record.qty_received_ext - record.qty_invoiced_ext,
                0
            )

    def _compute_invoice_lines_invoice_first_date(self):
        # TODO this computation doesn't look for related lines
        #      and their invoice dates
        for record in self:
            moves = record.invoice_lines.mapped("move_id")
            record.invoice_lines_invoice_first_date = (
                moves and moves.sorted("invoice_date")[0].invoice_date
                or False
            )

    def _compute_product_qty_readonly(self):
        for record in self:
            record.product_qty_readonly = (
                record.classified
            ) or (
                not record.classified
                and
                record.product_qty > record.pending_qty
            )

    @api.depends("date_planned")
    def _compute_date_planned_search(self):
        for record in self:
            record.date_planned_search = (
                record.date_planned and record.date_planned.date() or False
            )
