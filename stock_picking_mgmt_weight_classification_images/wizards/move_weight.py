# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
import base64
from io import BytesIO
from PIL import Image, ExifTags


class MoveWeight(models.TransientModel):
    _inherit = 'stock.move.weight.wizard'

    classification_image = fields.Image()
    dms_file_ids = fields.One2many(related='picking_id.dms_file_ids', readonly=False)

    def is_valid_base64_image(self, image_string):
        try:
            image = base64.b64decode(image_string)
            img = Image.open(BytesIO(image))
        except Exception:
            raise ValidationError(_("The file is not an image"))

        if img.format.lower() not in ["jpg", "jpeg"]:
            raise ValidationError(_("The image must be in jpg or jpeg format."))

    @api.onchange('classification_image')
    def _onchange_classification_image(self):
        if self.classification_image:
            self.is_valid_base64_image(self.classification_image)

            image = Image.open(BytesIO(base64.b64decode(self.classification_image)))
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            if image._getexif():
                exif = dict(image._getexif().items())

                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)

            buf = BytesIO()
            width, height = image.size

            side_max = max([width, height])
            side_min = min([width, height])
            porcent = (side_max - side_min) / side_max

            if width > height:
                width = self.env.company.picking_operations_imagen_max_resolution
                height = width - int(width * porcent)
            else:
                height = self.env.company.picking_operations_imagen_max_resolution
                width = height - int(height * porcent)

            image = image.resize((width, height))
            image.save(buf, format='JPEG', quality=self.env.company.picking_operations_imagen_quality)

            self.classification_image = base64.b64encode(buf.getvalue())

            storage_id = self.env.ref('stock_picking_mgmt_weight_classification_images.dms_storage_classification_image')
            group_id = self.env.ref('stock_picking_mgmt_weight_classification_images.dms_access_group_classification_image_manager')

            root_directory_id = self.env.ref('stock_picking_mgmt_weight_classification_images.dms_directory_classification_image')
            year_directory_id = root_directory_id.child_directory_ids.filtered(lambda x: x.name == fields.Datetime().now().strftime("%Y"))

            if not year_directory_id:
                year_directory_id = self.env['dms.directory'].sudo().create({
                    'name': fields.Datetime().now().strftime("%Y"),
                    'is_root_directory': False,
                    'storage_id': storage_id.id,
                    'parent_id': root_directory_id.id,
                    'group_ids': [(6, 0, [group_id.id])]
                })
            directory_id = year_directory_id.child_directory_ids.filtered(lambda x: x.name == fields.Datetime().now().strftime("%m"))
            file_name = '%s_%s' % (self.picking_id.name.replace('/', ''), fields.Datetime().now().strftime("%d%m%Y%H%M%S"))

            if not directory_id:
                directory_id = self.env['dms.directory'].sudo().create({
                    'name': fields.Datetime().now().strftime("%m"),
                    'is_root_directory': False,
                    'storage_id': storage_id.id,
                    'parent_id': year_directory_id.id,
                    'group_ids': [(6, 0, [group_id.id])]
                })

            dms_file_id = self.env['dms.file'].sudo().create({
                'name': file_name,
                'content': self.classification_image,
                'directory_id': directory_id.id,
                'classification_picking_id': self.picking_id.id
            })
            self.dms_file_ids = [(4, dms_file_id.id)]
            self.classification_image = False
