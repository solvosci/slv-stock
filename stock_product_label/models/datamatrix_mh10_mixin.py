# © 2026 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import models, fields
import io
import base64
from pylibdmtx.pylibdmtx import encode
from PIL import Image

class DatamatrixMh10Mixin(models.AbstractModel):
    _name = "datamatrix.mh10.mixin"
    _description = "datamatrix.mh10.mixin"

    mh10_data_encoded = fields.Binary(compute='_compute_mh10_data')

    def _compute_mh10_data(self):
        barcode_name = ''
        lot = ''
        for record in self:
            if record._name in ['product.template', 'product.product']:
                barcode_name = record.barcode
                lot = ''
            if record._name in ['product.label.lot.wizard', 'stock.quant']:
                barcode_name = record.product_id.barcode
                lot = record.lot_id.name
            if record._name in ['stock.move.line']:
                barcode_name = record.product_id.barcode
                lot = record.lot_id.name
            if record._name == 'stock.move':
                barcode_name = record.product_id.barcode
                lot = ''

            RS = chr(30) # \x1E
            GS = chr(29) # \x1D
            EOT = chr(4) # \x04

            header = f'[)>{RS}06{GS}'
            barcode_data = f"1P{barcode_name}"
            lot_data = f"{GS}1T{lot}"
            end_data = f"{RS}{EOT}"
            if not lot:
                data = header + barcode_data + end_data
            else:
                data = header + barcode_data + lot_data + end_data

            encoded = encode(data.encode('utf-8'))
            img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)

            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            record.mh10_data_encoded = base64.b64encode(buffer.getvalue())

    def get_label_template_xml_id(self):
        self.ensure_one()
        if self._name == "product.product":
            product = self.product_tmpl_id
        else:
            product = self

        template = (
            product.categ_id
            .product_label_template_id
            .qweb_template
        )

        if template and template.xml_id:
            return template.xml_id

        return "stock_product_label.label_generic_layout"
