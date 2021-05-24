# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError
                      

class PrecioHoras(models.Model):
    _name = "test_model_precio"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def default_employee2(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
     
    employee_id = fields.Many2one('hr.employee', string="Empleado", 
                                  default=default_employee2, required=True, 
                                  ondelete='cascade', index=True)
    fecha_precio = fields.Date("Fecha Creacion",  required=True)
    hora_lps = fields.Float("Precio Hora", required=True)
    horas_activo = fields.Boolean('Activo', required=True)
    tipo_hora = fields.Selection([('horanormal', 'Hora Normal'),('vacaciones', 'Hora Vacaciones')], 
                                   default="horanormal",
                                   string='Tipo Horas')
    