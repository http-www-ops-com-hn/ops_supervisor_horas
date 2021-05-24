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

class Ops_Inherints_Ausencias(models.Model):
    _inherit = "hr.leave"
    
    ops_ausencia_leave_id = fields.Many2one('test_model_asuencias_ops', string="Inicio De Asistencia", 
                                        ondelete='cascade', index=True)
    
    #Envio de correo al supervisor para decirle que ya esta aprobada la ausencia, 
    #Asi mismo cambiar la etapa de la asistencia a finalizado
    
    @api.multi
    def finalizar_proceso_asistencia(self):
        #Cambio la etapa a finalizado para que el colaborador y el supervisor logren ver en que etapa esta su solicitud
        stage = self.env['test_model_asuencias_ops'].search([('id', '=', self.ops_ausencia_leave_id.id)], limit=1)
        stage.write({'state':'validate'})
        #MUestra notificacion 
        self.env.user.notify_success(message='Se envio notificacion al supervisor.')
        return stage