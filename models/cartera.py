# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError
                      


class creacion_cartera_empleados(models.Model):
    _name = "test_model_cartera_tipo_ops"
    _order = 'nombre_cartera'
    _rec_name = 'nombre_cartera'

    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']
                                   
    nombre_cartera = fields.Char("Campaña")
    
    _sql_constraints = [
        ('name_uniq', 'unique (nombre_cartera)', "El nombre de la campaña ya existe !"),
    ]



class employee_cartera_nap(models.Model):
    _inherit = 'hr.employee'
    
    tipo_cartera_pro = fields.Many2one('test_model_cartera_tipo_ops', string="Tipo campaña", 
                                   ondelete='cascade', index=True)

    