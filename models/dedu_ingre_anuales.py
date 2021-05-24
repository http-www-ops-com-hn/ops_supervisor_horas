# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError


class DeduccionesAnuales(models.Model):
    _name = "model_tipo_dedu_ingre_anuales"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def default_employee2(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  default=default_employee2, required=True, 
                                  ondelete='cascade', index=True)
    
    tipo_dedu_id = fields.Many2one('hr.salary.rule', 
                                   string="Tipo Ingreso Anual",
                                   domain=[('category_id.code', '=', 'INGRE')],
                                   required=True, 
                                   ondelete='cascade', 
                                   index=True)
                                   
    tipo_activo = fields.Boolean(string="Activo", required=True)
    monto_lps = fields.Float(string="Monto Mensual", required=True)
    monto_year = fields.Float(string="Monto Anual", required=True)
    fecha_inicio = fields.Date(string="Fecha Inicio", required=True)

    tipo_moneda = fields.Selection([('Dolar', 'Dolares'),('Lempira', 'Lempiras')], 
                                   default="Lempira",
                                   string='Tipo Moneda')
