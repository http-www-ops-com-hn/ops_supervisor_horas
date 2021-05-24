# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import date
from datetime import datetime
from datetime import *
import datetime
from odoo.exceptions import UserError, ValidationError


class ConfiguracionesNomina(models.Model):
    _name = "model_configuraciones_nomina"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']
                                
    tipo_activo = fields.Boolean(string="Activo", required=True)
    monto_lps = fields.Float(string="IHSS Monto Quincenal", required=True)
    monto_ISR = fields.Float(string="IHSS Cobro de ISR", required=True)
    fecha = fields.Date(string="Fecha", required=True)
    techo_rap = fields.Float(string="Techo RAP", required=True)
    monto_minimo = fields.Float(string="Salario Minimo", required=True)
    monto_ihsspatrono = fields.Float(string="IHSS Patrono", required=True)
    