# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, models
import re

class WizStockBarcodesReadMH10(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _process_ai_1P(self, mh10_list):
        product_code = next((x['value'] for x in mh10_list if x['ai']=='1P'), None)
        if not product_code:
            return False
        product = self.env['product.supplierinfo'].search([('product_code','=',product_code)], limit=1).product_tmpl_id.product_variant_id
        if not product:
            product = self.env['product.product'].search([('barcode','=',product_code)], limit=1)
        if not product:
            self.message = _("Product %s not found") % product_code
            return False
        self.action_product_scaned_post(product)
        return True

    def _process_ai_1T(self, mh10_list):
        """Process Lot Code (1T)"""
        lot_name = next((x['value'] for x in mh10_list if x['ai']=='1T'), None)
        lot_id = self.env['stock.production.lot'].search([
            ('name','=', lot_name),
            ('product_id','=', self.product_id.id)
        ], limit=1)
        if not lot_id:
            lot_id = self.env['stock.production.lot'].create({
                'name': lot_name,
                'product_id': self.product_id.id
            })
        self.action_lot_scaned_post(lot_id)
        self.write({'lot_id': lot_id.id})
        return True

    def _process_ai_Q(self, mh10_list):
        """Process Quantity (Q)"""
        quantity = next((x['value'] for x in mh10_list if x['ai']=='Q'), None)
        self.write({'product_qty': quantity})
        return True

    def _get_enabled_mh10_ai(self):
        ai_map = {
            '1P': self.option_group_id.option_ids.filtered(lambda x: x.ansi_datamatrix_mh10 == '1P' and x.to_scan),
            '1T': self.option_group_id.option_ids.filtered(lambda x: x.ansi_datamatrix_mh10 == '1T' and x.to_scan),
            'Q': self.option_group_id.option_ids.filtered(lambda x: x.ansi_datamatrix_mh10 == 'Q' and x.to_scan),
        }
        return [ai for ai, enabled in ai_map.items() if enabled]

    def _barcode_is_mh10(self, barcode):
        return barcode.startswith('[)>06')

    def process_barcode(self, barcode):
        if self._barcode_is_mh10(barcode):
            mh10_list = []
            separator = r'\|'

            for ai in self._get_enabled_mh10_ai():
                match = re.search(rf'{ai}(?P<value>.*?)(?:{separator}|$)', barcode)
                if match:
                    mh10_list.append({'ai': ai, 'value': match.group('value').strip()})

            warning_msg_list = []
            self.message = False
            for mh10_item in mh10_list:
                ai = mh10_item['ai']
                if hasattr(self, f'_process_ai_{ai}'):
                    res = getattr(self, f'_process_ai_{ai}')(mh10_list)
                    if not res:
                        warning_msg_list.append(
                            self.message or _("({ai}) {barcode} Not found").format(
                                ai=ai, barcode=self.barcode
                            )
                        )
                        self.message = False
                else:
                    warning_msg_list.append(_("AI MH10 ({ai}) Not implemented").format(ai=ai))

            if warning_msg_list:
                self.barcode = False
                self._set_messagge_info("info", " ".join(warning_msg_list))
                for warning_msg in warning_msg_list:
                    self.display_notification(
                        warning_msg, message_type="danger", title="MH10 code"
                    )

            if not self.check_option_required():
                return False
            if self.is_manual_confirm or self.manual_entry:
                self._set_messagge_info("info", _("Review and confirm"))
                return False
            return self.action_confirm()

        return super().process_barcode(barcode)
