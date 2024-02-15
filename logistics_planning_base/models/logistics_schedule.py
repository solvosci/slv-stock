# © 2023 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import _, api, models, fields
from odoo.exceptions import ValidationError

import re

TRANSPORT_TYPE = [
    ('ground', 'Ground'),
    ('ocean-going', 'Ocean-Going'),
]
PRICE_UNIT_TYPES = [
    ("trip", "Trip"),
    ("unit", "Unit"),
]
LICENSE_PLATE_RE = "^\w+$"


class LogisticsSchedule(models.Model):
    _name = 'logistics.schedule'
    _description = 'logistics.schedule'
    _order = "scheduled_load_date desc, id desc"

    # Only editable in draft mode
    READONLY1_STATES = {
        "ready": [("readonly", True)],
        "cancel": [("readonly", True)],
        "done": [("readonly", True)],
    }
    # Only editable in ready mode
    READONLY2_STATES = {
        "draft": [("readonly", True)],
        "cancel": [("readonly", True)],
        "done": [("readonly", True)],
    }
    # Readonly when not pending
    READONLY3_STATES = {
        "cancel": [("readonly", True)],
        "done": [("readonly", True)],
    }

    name = fields.Char(compute='_compute_name')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('ready', 'Ready'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
        ],
        default='draft',
        tracking=True,
    )
    type = fields.Selection(
        selection=[
            ('input', 'Input'),
            ('output', 'Output'),
        ],
        states=READONLY1_STATES,
    )
    origin = fields.Char(
        readonly=True,
        help="""
        Origin document (e.g. purchase order for inputs, sales order for outputs,...)
        """,
    )
    stock_move_id = fields.Many2one('stock.move', states=READONLY2_STATES)
    picking_id = fields.Many2one('stock.picking', related='stock_move_id.picking_id', store=True)
    destination_partner_id = fields.Many2one(
        'res.partner',
        string="Destination",
        states=READONLY3_STATES,
    )
    partner_id = fields.Many2one('res.partner', states=READONLY1_STATES)
    transport_type = fields.Selection(
        selection=TRANSPORT_TYPE,
        states=READONLY1_STATES,
    )
    product_id = fields.Many2one(
        'product.product',
        domain="[('type', 'in', ['product', 'consu'])]",
        states=READONLY1_STATES,
    )
    # TODO set as related? Default value?
    product_uom = fields.Many2one('uom.uom', readonly=True)
    product_uom_qty = fields.Float(
        digits='Product Unit of Measure',
        string="Quantity",
        compute="_compute_product_uom_qty",
        store=True,
        readonly=False,
        states=READONLY3_STATES,
    )
    scheduled_load_date = fields.Date(states=READONLY1_STATES)
    commitment_date = fields.Datetime(states=READONLY2_STATES)
    commitment_date_hour = fields.Float(states=READONLY2_STATES)
    effective_date = fields.Datetime(states=READONLY2_STATES)
    logistics_price_unit_type = fields.Selection(
        selection=PRICE_UNIT_TYPES,
        string="Price Type",
        states=READONLY1_STATES,
    )
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    logistics_price_unit = fields.Float(
        digits='Product Price',
        string="Price unit",
        states=READONLY1_STATES,
    )
    logistics_price_unit_done = fields.Float(
        digits='Product Price',
        string="Price Unit Done",
        states=READONLY2_STATES,
    )
    carrier_id = fields.Many2one(
        'res.partner',
        string="Carrier",
        states=READONLY3_STATES,
    )
    effective_carrier_id = fields.Many2one(
        'res.partner',
        string="Effective Carrier",
        states=READONLY3_STATES,
    )
    license_plate_1 = fields.Char(states=READONLY3_STATES)
    license_plate_2 = fields.Char(states=READONLY3_STATES)
    schedule_finished = fields.Boolean(states=READONLY2_STATES)
    note = fields.Text()

    can_set_to_done = fields.Boolean(
        compute="_compute_can_set_to_done",
        help="""
        Tecnical field indicating whether this record can be set to done state
        """,
    )

    def _compute_name(self):
        # TODO improve name // move to name_get()
        for record in self:
            record.name = f'{record.carrier_id.name} ({record.partner_id.name}) // {record.picking_id.name} - {record.product_id.display_name}'

    def _compute_can_set_to_done(self):
        to_done = self.filtered(lambda x: x.state == "ready")
        to_done.write({"can_set_to_done": True})
        (self - to_done).write({"can_set_to_done": False})

    @api.onchange("product_id")
    def _onchange_product_id(self):
        # For manual logistics schedules
        self.product_uom = self.product_id.uom_id

    @api.depends("stock_move_id.product_uom_qty")
    def _compute_product_uom_qty(self):
        for record in self.filtered(lambda x: x.stock_move_id):
            record.product_uom_qty = record.stock_move_id.product_uom_qty

    @api.onchange("stock_move_id")
    def _onchange_stock_move_id(self):
        self.ensure_one()
        if self.stock_move_id:
            self.write({
                "commitment_date": self.stock_move_id.date,
                "schedule_finished": True,
            })

    @api.onchange("carrier_id")
    def _onchange_carrier_id(self):
        # TODO move effective_carrier_id to compute stored?
        self.ensure_one()
        if self.carrier_id and not self.effective_carrier_id:
            self.effective_carrier_id = self.carrier_id

    @api.constrains("commitment_date_hour")
    def _check_commitment_date_hour(self):
        invalid_hours = self.filtered(
            lambda x: not (0 < x.commitment_date_hour < 24)
        )
        if invalid_hours:
            raise ValidationError(_(
                "Commitment hour invalid. Accepted values between 00:00"
                " and 23:59"
            ))

    @api.onchange("license_plate_1")
    def _check_license_plate_1(self):
        self._check_license_plate_valid("license_plate_1")

    @api.onchange("license_plate_2")
    def _check_license_plate_2(self):
        self._check_license_plate_valid("license_plate_2")

    def _check_license_plate_valid(self, license_plate_field):
        license_plate = self[license_plate_field]
        if license_plate and not re.match(LICENSE_PLATE_RE, license_plate):
            self[license_plate_field] = False
            raise ValidationError(
                _("Wrong license plate: [%s] (only alphanumeric characters are valid)")
                % license_plate
            )

    def action_logistics_schedule_form_view(self):
        # action = self.env.ref('logistics_planning_base.action_logistics_schedule_form')
        # action_logistics_schedule_input
        action = self.env.ref(
            "logistics_planning_base.action_logistics_schedule_%s_form"
            % self.env.context["default_type"]
        )
        result = action.read()[0]
        result["res_id"] = self.id
        return result

    def action_logistics_schedule_ready(self):
        self.browse(self.env.context.get("active_ids", [])).with_context(
            ls_check_req_fields=True
        )._action_ready()

    def action_logistics_schedule_cancel(self):
        self.browse(self.env.context.get("active_ids", []))._action_cancel()

    def action_logistics_schedule_done(self):
        self.browse(self.env.context.get("active_ids", []))._action_done()

    def _action_ready(self):
        to_ready = self.filtered(lambda x: x.state in ["draft", "cancel"])
        if self.env.context.get("ls_check_req_fields", False):
            req_fields = self._action_ready_fields_check_req_fields()
            for ls in to_ready:
                ok = all([ls[field] for field in req_fields])
                if not ok:
                    raise ValidationError(
                        _(
                            "Cannot mark schedule(s) as ready: there's at least one"
                            "required field unset. Required fields:\n\n- %s"
                        ) % "\n- ".join(req_fields.values())
                    )
        to_ready.write({"state": "ready"})
        return to_ready

    def _action_ready_fields_check_req_fields(self):
        return {
            "partner_id": _("Contact (Provider/Vendor)"),
            "transport_type": _("Transport type"),
            "product_id": _("Product"),
            "scheduled_load_date": _("Scheduled Date"),
            "logistics_price_unit_type": _("Price Type"),
        }

    def _action_cancel(self):
        to_cancel = self.filtered(lambda x: x.state in ['draft', 'ready', 'done'])
        to_cancel.write({
            "state": "cancel",
            "stock_move_id": False,
            "schedule_finished": False,
        })
        return to_cancel

    def _action_done(self, skip_can_set_to_done=False):
        to_done = self
        if not skip_can_set_to_done:
            to_done = to_done.filtered(lambda x: x.can_set_to_done)
        to_done_wo_sm = to_done.filtered(lambda x: not x.stock_move_id)
        if len(to_done_wo_sm) > 0:
            raise ValidationError(_(
                "There's at least one schedule without stock move filled"
            ))
        to_done_wo_s_finished = to_done.filtered(
            lambda x: not x.schedule_finished
        )
        if len(to_done_wo_s_finished) > 0:
            raise ValidationError(_(
                "There's at least one schedule unmarked as finished"
            ))
        to_done.write({"state": "done"})
        return to_done

    def write(self, values):
        if "stock_move_id" in values:
            # We assume that only a record is selected, no "expected singleton" should be fired
            # (1) If there was a previous stock move linked, ls should be unlinked
            if self.stock_move_id:
                self.stock_move_id.logistics_schedule_id = False
            # (2) If a new stock move is linked => ls should be linked as well
            if values.get("stock_move_id", False):
                self.env['stock.move'].browse(
                    values["stock_move_id"]
                ).logistics_schedule_id = self
            # (3) If stock move was actually removed => nothing else to do
        return super().write(values)
