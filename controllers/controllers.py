# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json


class IngresosController(http.Controller):

    @http.route('/api/ingresos', auth='public', method=['GET'], csrf=False)
    def get_visits(self, **kw):
        try:
            ingresos = http.request.env['test_model_ingresos'].sudo().search_read([], ['id', 'employee_id'])
            res = json.dumps(ingresos, ensure_ascii=False).encode('utf-8')
            return Response(res, content_type='application/json;charset=utf-8', status=200)
        except Exception as e:
            return Response(json.dumps({'error': str(e)}), content_type='application/json;charset=utf-8', status=505)