# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError
                      


class creacion_proyectos_empleados(models.Model):
    _name = "test_model_proyectos_tipo_ops"
    _order = 'nombre_proyecto'
    _rec_name = 'nombre_proyecto'

    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']
                                   
    nombre_proyecto = fields.Char("Proyecto")

    tipo_cartera_pro = fields.Many2one('test_model_cartera_tipo_ops', 
                                   string="Tipo campaña", 
                                   ondelete='cascade', 
                                   index=True)

    _sql_constraints = [
        ('name_uniq', 'unique (nombre_proyecto)', "El nombre del proyecto ya existe !"),
    ]


class creacion_sub_proyectos_empleados(models.Model):
    _name = "test_model_sub_proyectos_tipo_ops"
    _order = 'nombre_subproyecto'
    _rec_name = 'nombre_subproyecto'

    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']
                                   
    nombre_subproyecto = fields.Char("Subproyecto")
    
    tipo_proyecto_pro = fields.Many2one('test_model_proyectos_tipo_ops', 
                                   string="Tipo Proyecto", 
                                   ondelete='cascade', 
                                   index=True)

    
    _sql_constraints = [
        ('name_uniq', 'unique (nombre_subproyecto)', "El nombre del subproyecto ya existe !"),
    ]

class employee_proyectos_nap(models.Model):
    _inherit = 'hr.employee'
    
    tipo_proyecto_id_pro = fields.Many2one('test_model_proyectos_tipo_ops', 
                                   string="Tipo Proyecto", 
                                   ondelete='cascade', 
                                   index=True)
    
    sub_tipo_proyecto_id_pro = fields.Many2one('test_model_sub_proyectos_tipo_ops', 
                                   string="Tipo Subproyecto", 
                                   ondelete='cascade', 
                                   index=True)


    @api.onchange('tipo_cartera_pro')
    def _onchange_cartera_id(self):
        if self.tipo_cartera_pro:
           self.tipo_proyecto_id_pro = False
           self.sub_tipo_proyecto_id_pro = False
           for rec in self:
               return {'domain': {'tipo_proyecto_id_pro': [('tipo_cartera_pro.id', '=', rec.tipo_cartera_pro.id)]}}


    @api.onchange('tipo_proyecto_id_pro')
    def _onchange_proyecto_id(self):
        if self.tipo_proyecto_id_pro:
           self.sub_tipo_proyecto_id_pro = False
           for rec in self:
               return {'domain': {'sub_tipo_proyecto_id_pro': [('tipo_proyecto_pro.id', '=', rec.tipo_proyecto_id_pro.id)]}}
