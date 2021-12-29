# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3.0 (https://www.gnu.org/licenses/lgpl-3.0.html)

from odoo import models, fields, _


class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    in_scale_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='In Type Scale',
        check_company=True)
    out_scale_type_id = fields.Many2one(
        comodel_name='stock.picking.type',
        string='Out Type Scale',
        check_company=True)

    def _get_sequence_values(self):
        sequence = super()._get_sequence_values()

        sequence['in_scale_type_id'] = {
            'name': self.name + ' ' + _('Sequence Scale in'),
            'prefix': self.code + '/INS/', 'padding': 5,
            'company_id': self.company_id.id}
        sequence['out_scale_type_id'] = {
            'name': self.name + ' ' + _('Sequence Scale out'),
            'prefix': self.code + '/OUTS/', 'padding': 5,
            'company_id': self.company_id.id}

        return sequence

    def _get_picking_type_update_values(self):
        picking_type = super()._get_picking_type_update_values()
        input_loc, output_loc = \
            self._get_input_output_locations(
                self.reception_steps, self.delivery_steps)
        scale_operation_in = {'default_location_dest_id': input_loc.id}
        scale_operation_out = {'default_location_src_id': output_loc.id}
        picking_type['in_scale_type_id'] = scale_operation_in
        picking_type['out_scale_type_id'] = scale_operation_out

        return picking_type

    def _get_picking_type_create_values(self, max_sequence):
        picking_type, max_sequence_new = \
            super()._get_picking_type_create_values(max_sequence)
        scale_operation_in = {
            'name': _('Scale Receipts'),
            'code': 'incoming',
            'use_create_lots': True,
            'use_existing_lots': False,
            'default_location_src_id': False,
            'sequence': max_sequence_new,
            'barcode': self.code.replace(" ", "").upper() + "-SC-RECEIPTS",
            'show_reserved': False,
            'sequence_code': 'INS',
            'company_id': self.company_id.id,
            'scale': True
        }
        scale_operation_out = {
            'name': _('Scale Delivery Orders'),
            'code': 'outgoing',
            'use_create_lots': False,
            'use_existing_lots': True,
            'default_location_dest_id': False,
            'sequence': max_sequence_new + 1,
            'barcode': self.code.replace(" ", "").upper() + "-SC-DELIVERY",
            'sequence_code': 'OUTS',
            'company_id': self.company_id.id,
            'scale': True
        }
        picking_type['in_scale_type_id'] = scale_operation_in
        picking_type['out_scale_type_id'] = scale_operation_out
        return picking_type, max_sequence + 2
