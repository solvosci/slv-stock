# © 2024 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from odoo.addons.logistics_planning_base.models.logistics_schedule import TRANSPORT_TYPE

class LogisticsSchedule(models.Model):
    _inherit = 'logistics.schedule'

    account_move_line_id = fields.Many2one('account.move.line', readonly=True)
    account_move_id = fields.Many2one('account.move', related='account_move_line_id.move_id', string='Invoice')
    is_invoiceable = fields.Boolean(compute='_compute_is_invoiceable', store=True)
    is_finished = fields.Boolean()

    def write(self, values):
        if "is_finished" in values and values['is_finished']:
            self.state = 'done'
        return super().write(values)

    @api.depends('account_move_line_id', 'state')
    def _compute_is_invoiceable(self):
        for record in self:
            if record.account_move_line_id or record.state == 'done':
                record.is_invoiceable = False
            else:
                record.is_invoiceable = True

    def _compute_can_set_to_done(self):
        # Schedules that are initially set to done available, but can be invoiced,
        #  _must be_ invoiced to be done
        super()._compute_can_set_to_done()
        to_not_done = self.filtered(
            lambda x: x.can_set_to_done and x.is_invoiceable
        )
        to_not_done.write({"can_set_to_done": False})

    def _action_cancel(self):
        to_cancel = super()._action_cancel()
        not_cancellable = to_cancel.filtered(lambda x: x.account_move_line_id)
        if not_cancellable:
            raise ValidationError(_(
                "There are %d schedule(s) already invoiced,"
                " please first unselect them"
            ) % len(not_cancellable))
        return to_cancel

    # def is_invoiceable(self):
    #     return not any(
    #         record.account_move_line_id or record.state == 'done'
    #         for record in self
    #     )

    def action_create_invoice_wizard(self):
        if not self.env.user.has_group("account.group_account_user") and not self.env.user.has_group("account.group_account_manager"):
            raise ValidationError(_('You need invoice user access to perform this action.'))

        lg_ids = self.browse(self.env.context.get('active_ids')).filtered(lambda x: x.is_invoiceable)
        carrier_id = lg_ids.mapped('carrier_id')

        if not lg_ids:
            raise ValidationError(_('No invoiceable schedules were selected.'))
        
        if lg_ids.filtered(lambda x: not x.stock_move_id):
            raise ValidationError(_("There are at least one schedule without stock move selected"))
        if lg_ids.filtered(lambda x: not x.carrier_id):
            raise ValidationError(_("There are at least one schedule without carrier selected"))
        if lg_ids.filtered(lambda x: not x.schedule_finished):
            raise ValidationError(_("There are at least one schedule unmarked as finished"))

        if len(carrier_id) > 1:
            raise ValidationError(_('You cannot select multiple schedules with different carriers.'))

        Wizard = self.env['logistics.schedule.account.move.wizard']
        new = Wizard.create({
            'logistics_schedule_ids': lg_ids.ids,
            'carrier_id': carrier_id.id
        })
        return {
            'name': _('Create Invoice'),
            'res_model': 'logistics.schedule.account.move.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': new.id,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def _prepare_ls_account_move(self):
        return {
            'default_type': 'in_invoice',
            'default_company_id': self.company_id.id,
            'default_logistics_schedule_ids': self.ids,
        }

    def _prepare_ls_account_move_line(self, move_id):
        self.ensure_one()
        ls_id = self.browse(self.id.origin)
        if ls_id.logistics_price_unit_type == 'trip':
            qty = 1
        else:
            qty = ls_id.product_uom_qty

        product = self._get_invoice_product()
        return {
            'name': '%s: %s' % (ls_id.picking_id.name or '', ls_id.product_id.name),
            'move_id': move_id.id,
            'currency_id': ls_id.currency_id.id,
            'logistics_schedule_id': ls_id.id,
            'product_id': product.id,
            'product_uom_id': product.uom_id.id,
            'price_unit': ls_id.logistics_price_unit_done,
            'quantity': qty,
            'partner_id': ls_id.partner_id.id,
        }

    def _get_invoice_product(self):
        self.ensure_one()
        if self.type == "input" and self.transport_type == TRANSPORT_TYPE[0][0]:
            return self.env.company.ls_default_inv_i_g_product_id
        elif self.type == "input" and self.transport_type == TRANSPORT_TYPE[1][0]:
            return self.env.company.ls_default_inv_i_og_product_id
        elif self.type == "output" and self.transport_type == TRANSPORT_TYPE[0][0]:
            return self.env.company.ls_default_inv_o_g_product_id
        elif self.type == "output" and self.transport_type == TRANSPORT_TYPE[1][0]:
            return self.env.company.ls_default_inv_o_og_product_id
        else:
            return False
