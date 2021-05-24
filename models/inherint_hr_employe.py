import logging
import math

from collections import namedtuple

from datetime import datetime, time
from pytz import timezone, UTC

from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

tipo_camisas = [
    ('xs', 'xs'),
    ('s', 's'),
    ('m', 'm'),
    ('l', 'l'),
    ('xl', 'xl'),
    ('xxl', 'xxl'),
]

personas_depen = [
    ('0', '0'),
    ('1', '1'),
    ('2', '2'),
    ('3', '3'),
    ('4', '4'),
    ('5', '5'),
    ('7', '7'),
    ('8', '8'),
    ('9', '9'),
    ('10', '10'),
]

seleccion_si = [
    ('SI', 'SI'),
    ('NO', 'NO'),
]


class Ops_Inherints_empleados(models.Model):
    _inherit = "hr.employee"

    
    dimension = fields.Char("Dimension")
    tipo_camisa = fields.Selection(tipo_camisas, string='Talla Camisa', index=True, default=tipo_camisas[0][0])
    rtn_emple = fields.Char("RTN")
    correo_personals = fields.Char("Correo Personal")
    cuenta_bancaria_personal = fields.Char("# Cuenta Bancaria")
    


    descri_ingreso = fields.Char("Descripción de ingresos")
    personas_dependen = fields.Selection(personas_depen, string='¿Cuántas personas dependen económicamente de usted?', index=True, default=personas_depen[0][0])
   
   
    vive_en_casa = fields.Selection(seleccion_si, string='Vive en casa propia', index=True, default=seleccion_si[0][0])
    paga_renta = fields.Selection(seleccion_si, string='Paga Renta', index=True, default=seleccion_si[0][0])
    
    renta_mensual = fields.Char("Renta Mensual")
    pariente_trabaja =  fields.Selection(seleccion_si, string='Algun pariente trabaja en esta empresa', index=True, default=seleccion_si[0][0]) 
    
    periente_ops = fields.Char("Nombre del pariente que labora en OPS")
    auto_propio = fields.Selection(seleccion_si, string='Posee automóvil propio', index=True, default=seleccion_si[0][0]) 


    tiene_otro_ingreso = fields.Selection(seleccion_si, string='Tiene otro ingreso', index=True, default=seleccion_si[0][0])
    

    tiene_deudas = fields.Selection(seleccion_si, string='Tiene deudas', index=True, default=seleccion_si[0][0])

    domicilio_he = fields.Char("Domicilio")
    fecha_ingreso = fields.Date("Fecha Ingreso")
    profesion_hn = fields.Char("Profesion")
    no_cartera = fields.Boolean('No pertenece a campañas', default=False)



    _sql_constraints = [
        ('name_uniq', 'unique (identification_id)', "El numero de identidad ya existe !"),
    ]
    