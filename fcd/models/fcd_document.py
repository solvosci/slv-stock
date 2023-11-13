# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields, api


class FcdDocument(models.Model):
    _name ='fcd.document'
    _description = 'fcd.document'

    name = fields.Char(required=True)
    fcd_document_line_ids = fields.One2many(comodel_name='fcd.document.line', inverse_name='fcd_document_id')
    scientific_name = fields.Char(related='product_id.scientific_name')
    fao = fields.Char(related='product_id.fao')
    fao_zone = fields.Char()
    subzone_id = fields.Many2one('fcd.fao.subzone')
    subzone = fields.Char()
    specific_lot = fields.Char()
    internal_lot_id = fields.Many2one('stock.production.lot')
    packaging_date = fields.Date()
    expiration_date = fields.Date()
    fishing_gear_id = fields.Many2one('fcd.fishing.gear')
    fishing_gear = fields.Char()
    production_method_id = fields.Many2one('fcd.production.method')
    production_method = fields.Char() #fields.Many2one('fcd.production.method')
    presentation_id = fields.Many2one('fcd.presentation')
    presentation = fields.Char()
    presentation_code = fields.Char(compute="_compute_presentation_code", store=True, string="CodAlpha3")
    ship_id = fields.Many2one('fcd.ship')
    ship = fields.Char()
    ship_license_plate = fields.Char()
    ship_country = fields.Many2one('res.country', string='Origin')
    tide_start_date = fields.Date()
    tide_end_date = fields.Date()
    packing = fields.Char()
    sanity_reg = fields.Char()

    product_id = fields.Many2one('product.product')
    partner_id = fields.Many2one('res.partner', string="Supplier")
    commercial_margin = fields.Char()

    qc_inspection_ids = fields.One2many('qc.inspection', 'fcd_document_id', string='Inspection')
    created_inspections = fields.Integer(compute="_compute_count_inspections", string="Total")
    done_inspections = fields.Integer(compute="_compute_count_inspections", string="Done inspections")
    passed_inspections = fields.Integer(compute="_compute_count_inspections", string="OK")
    failed_inspections = fields.Integer(compute="_compute_count_inspections", string="Failed")

    notes = fields.Text()
    notes_fishing = fields.Text()
    notes_quality = fields.Text()

    @api.onchange('subzone_id')
    def _onchange_subzone_id(self):
        self.fao_zone = self.subzone_id.name

    @api.onchange('fishing_gear_id')
    def _onchange_fishing_gear_id(self):
        self.fishing_gear = self.fishing_gear_id.name

    @api.onchange('presentation_id')
    def _onchange_presentation_id(self):
        self.presentation = self.presentation_id.name

    @api.onchange('production_method_id')
    def _onchange_production_method_id(self):
        self.production_method = self.production_method_id.name

    @api.onchange('ship_id')
    def _onchange_ship_id(self):
        self.ship = self.ship_id.name
        self.ship_license_plate = self.ship_id.license_plate

    @api.depends('presentation')
    def _compute_presentation_code(self):
        for record in self:
            presentation_id = self.env['fcd.presentation'].search([('name', '=', record.presentation)])
            if presentation_id:
                record.presentation_code = presentation_id.code
            else:
                record.presentation_code = False

    def _compute_count_inspections(self):
        for record in self:
            record.created_inspections = len(record.qc_inspection_ids)
            record.done_inspections = len(record.qc_inspection_ids.filtered(
                lambda x: x.state in ['success', 'failed'])
            )
            record.passed_inspections = len(record.qc_inspection_ids.filtered(
                lambda x: x.state == 'success')
            )
            record.failed_inspections = len(record.qc_inspection_ids.filtered(
                lambda x: x.state == 'failed')
            )

    def _get_inspection_context(self, domain):
        self.ensure_one()
        ctx = {
            'name': ('Stock Quant'),
            'res_model': 'qc.inspection',
            'domain': domain,
            'target': 'current',
            'type': 'ir.actions.act_window',
            'context': {
                'default_object_id': ('fcd.document,{}'.format(self.id)),
                'default_test': self.env.ref('fcd.fcd_qc_fish_entry').id,
                'fcd': True,
            }
        }
        if self.created_inspections == 0:
            ctx['view_mode'] = 'form'
        else:
            ctx['view_mode'] = 'tree,form'
        return ctx


    def action_calculate_inspection_context(self):
        """Calculate the inspection context of the document."""
        domain = [('fcd_document_id', '=', self.id)]
        return self._get_inspection_context(domain)

    def action_calculate_inspection_done_context(self):
        """Calculate the inspection context of the done documents."""
        domain = [('fcd_document_id', '=', self.id), ('state', 'not in', ['draft', 'waiting'])]
        return self._get_inspection_context(domain)

    def action_calculate_inspection_passed_context(self):
        """Calculate the inspection context of the passed documents."""
        domain = [('fcd_document_id', '=', self.id),('state', '=', 'success')]
        return self._get_inspection_context(domain)

    def action_calculate_inspection_failed_context(self):
        """Calculate the inspection context of the failed documents."""
        domain = [('fcd_document_id', '=', self.id),('state', '=', 'failed')]
        return self._get_inspection_context(domain)
