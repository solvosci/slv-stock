# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, http
from odoo.http import request


class CameraController(http.Controller):

    @http.route(
        "/stock_picking_mgmt_weight/camera/read",
        type="json",
        auth="none",
    )
    def read(self):
        # TODO test it in a multi-company environment and user
        camera_id = request.env['res.users'].search([
            ('id', '=', request.session.uid)
        ]).company_id.picking_operations_camera_id

        return {"url_image": camera_id.sudo().url,
                "refresh_time": camera_id.sudo().refresh_time}
