# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError

class Tpo_Iingresos(models.Model):
    _name = "test_model_tipo_ingresos"
    _order = 'nombre_dedu'
    _rec_name = 'nombre_dedu'

    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    nombre_dedu = fields.Text("Nombre Ingresos",  required=True)
    tipo_activo = fields.Boolean('Activo', required=True)

class IngresosHoras(models.Model):
    _name = "test_model_ingresos"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def default_employee2(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  default=default_employee2, required=True, 
                                  ondelete='cascade', index=True)
    
    tipo_ingre_id = fields.Many2one('hr.salary.rule', 
                                   string="Tipo Ingreso", 
                                   required=True, 
                                   ondelete='cascade', 
                                   index=True)
                                   
    fecha_precio = fields.Date("Fecha Creacion",  required=True)
    monto_lps = fields.Float("Monto", required=True)