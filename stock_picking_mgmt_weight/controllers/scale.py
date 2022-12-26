# © 2021 Solvos Consultoría Informática (<http://www.solvos.es>)
# License LGPL-3 - See https://www.gnu.org/licenses/lgpl-3.0.html

from odoo import _, http
from odoo.http import request


class ScaleController(http.Controller):

    @http.route(
        "/stock_picking_mgmt_weight/scale/read",
        type="json",
        auth="none",
    )
    def read(self):
        # TODO test it in a multi-company environment and user
        # scale_id = request.env['res.users'].search([
        #     ('id', '=', request.session.uid)
        # ]).company_id.picking_operations_scale_id

        # return scale_id and scale_id.sudo().get_weight() or {
        #     "value": "----",
        #     "err": _("Undefined scale for current company")
        # }
        scale_id = request.env['res.users'].search([
            ('id', '=', request.session.uid)
        ]).company_id.sudo().picking_operations_scale_id
        if not scale_id:
            return {
                "value": "----",
                "err": _("Undefined scale for current company"),
            }
        ret = request.env["scale.scale"]._run_scheduler_once(scale_id)
        if ret.get("last_weight_error", False):
            return {
                "value": "----",
                "err": ret["last_weight_error"],
            }
        else:
            return {
                "value": ret["last_weight"],
                "ok": ret["last_weight_ok"],
                "err": False,
            }
