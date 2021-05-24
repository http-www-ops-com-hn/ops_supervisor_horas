# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError


class ComisionesEstimado(models.Model):
    _name = "comisiones_estimado"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  required=True, 
                                  ondelete='cascade', index=True)
    
                                   
    tipo_activo = fields.Boolean(string="Activo", required=True)
    monto_lps = fields.Float(string="Comisiones Estimado Mensual", required=True)
    year_sueldo = fields.Integer(string='Año', required=True) 

    