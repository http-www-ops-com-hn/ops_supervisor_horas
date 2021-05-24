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

# See _onchange_request_parameters
DummyAttendance = namedtuple('DummyAttendance', 'hour_from, hour_to, dayofweek, day_period')


class Ops_ausencias_Solicitud(models.Model):
    _name = "test_model_asuencias_ops"
    #Esta herencia funciona para que se pueda mostrar el pie de pagina en los formularios con las notas y poder enviar correos
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        return self.env.context.get('default_employee_id') or self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    #employee_id = fields.Many2one('res.users', string='Empleado', default=lambda self: self.env.user, track_visibility="onchange")
    employee_id = fields.Many2one('hr.employee', string='Empleado', index=True, readonly=True,
                                    states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, default=_default_employee, track_visibility='onchange')
    manager_id = fields.Many2one('hr.employee', string='Gerente', readonly=True)
    user_id = fields.Many2one('res.users', string='Usuario', related='employee_id.user_id', related_sudo=True, compute_sudo=True, store=True, default=lambda self: self.env.uid, readonly=True)

   
    notas = fields.Text("Descripcion")
    
    holiday_type = fields.Selection([
        ('employee', 'Por empleado'),
        ('company', 'Por empresa'),
        ('department', 'Por departamento'),
        ('category', 'Por etiqueta de empleado')],
        string='Modo de asignación', readonly=True, required=True, default='employee',
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
        help="Allow to create requests in batchs:\n- By Employee: for a specific employee"
             "\n- By Company: all employees of the specified company"
             "\n- By Department: all employees of the specified department"
             "\n- By Employee Tag: all employees of the specific employee group category")

    
    mode_company_id = fields.Many2one('res.company', string='Compañia', readonly=True)
    #Informacion depto
    #@api.onchange('employee_id')
    @api.multi
    def default_depto(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.department_id
    
    department_id = fields.Many2one('hr.department', string='Departamento', default=default_depto)
    
    #@api.onchange('employee_id')
    #@api.multi
    # def _onchange_employee(self):
    #    if self.holiday_type == 'employee':
    #        self.department_id = self.employee_id.department_id
    
    #Informacion cartera
    #@api.onchange('employee_id')
    @api.multi
    def default_cartera(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.tipo_cartera_pro
    
    cartera_id = fields.Many2one('test_model_cartera_tipo_ops', string='Cartera', default=default_cartera)
    
    #Informacion tipo_proyecto
    #@api.onchange('employee_id')
    @api.multi
    def default_proyecto(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.tipo_proyecto_id_pro
    
    proyecto_id = fields.Many2one('test_model_proyectos_tipo_ops', string='Proyecto', default=default_proyecto)

    #Obtener supervisor
    #@api.onchange('employee_id')
    @api.multi
    def default_supervisor(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.coach_id

    supervisor_id = fields.Many2one('hr.employee', string="Supervisor", required=True, default=default_supervisor, 
                                  ondelete='cascade', index=True)

    # leave type configuration
    holiday_status_id = fields.Many2one("hr.leave.type", string="Tipo de ausencia", required=True, readonly=True,
                                         states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]},
                                         domain=[('valid', '=', True)])
    
    validation_type = fields.Selection('Tipo de validación', related='holiday_status_id.validation_type', readonly=False)

    #state
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Enviado Supervisor'),
        ('confirm2', 'Enviado RRHH'),
        ('validate', 'Aprobacion'),
         ('cancel', 'Rechazado')
        ], string='Etapa', readonly=True, track_visibility='onchange', copy=False, default='draft',
        help="The status is set to 'To Submit', when a leave request is created." +
        "\nThe status is 'To Approve', when leave request is confirmed by user." +
        "\nThe status is 'Refused', when leave request is refused by manager." +
        "\nThe status is 'Approved', when leave request is approved by manager.")
    
    name = fields.Char('Descripcion')

    leave_type_request_unit = fields.Selection(related='holiday_status_id.request_unit', readonly=True)

    # duracion
    date_from = fields.Datetime('Desde', readonly=True, index=True, copy=False, required=True,
                                default=fields.Datetime.now,
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, 
                                track_visibility='onchange')
    
    date_to = fields.Datetime('Hasta', readonly=True, copy=False, required=True,
                                default=fields.Datetime.now,
                                states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, 
                                track_visibility='onchange')


    # Interface fields used when not using hour-based computation
    request_date_from = fields.Date('Solicitar fecha de inicio')
    request_date_to = fields.Date('Solicitar fecha de finalización')
    
      #
    request_hour_from = fields.Selection([
        (0, '12:00 AM'), (-1, '0:30 AM'),
        (1, '1:00 AM'), (-2, '1:30 AM'),
        (2, '2:00 AM'), (-3, '2:30 AM'),
        (3, '3:00 AM'), (-4, '3:30 AM'),
        (4, '4:00 AM'), (-5, '4:30 AM'),
        (5, '5:00 AM'), (-6, '5:30 AM'),
        (6, '6:00 AM'), (-7, '6:30 AM'),
        (7, '7:00 AM'), (-8, '7:30 AM'),
        (8, '8:00 AM'), (-9, '8:30 AM'),
        (9, '9:00 AM'), (-10, '9:30 AM'),
        (10, '10:00 AM'), (-11, '10:30 AM'),
        (11, '11:00 AM'), (-12, '11:30 AM'),
        (12, '12:00 PM'), (-13, '0:30 PM'),
        (13, '1:00 PM'), (-14, '1:30 PM'),
        (14, '2:00 PM'), (-15, '2:30 PM'),
        (15, '3:00 PM'), (-16, '3:30 PM'),
        (16, '4:00 PM'), (-17, '4:30 PM'),
        (17, '5:00 PM'), (-18, '5:30 PM'),
        (18, '6:00 PM'), (-19, '6:30 PM'),
        (19, '7:00 PM'), (-20, '7:30 PM'),
        (20, '8:00 PM'), (-21, '8:30 PM'),
        (21, '9:00 PM'), (-22, '9:30 PM'),
        (22, '10:00 PM'), (-23, '10:30 PM'),
        (23, '11:00 PM'), (-24, '11:30 PM')], string='Hour from')
    request_hour_to = fields.Selection([
        (0, '12:00 AM'), (-1, '0:30 AM'),
        (1, '1:00 AM'), (-2, '1:30 AM'),
        (2, '2:00 AM'), (-3, '2:30 AM'),
        (3, '3:00 AM'), (-4, '3:30 AM'),
        (4, '4:00 AM'), (-5, '4:30 AM'),
        (5, '5:00 AM'), (-6, '5:30 AM'),
        (6, '6:00 AM'), (-7, '6:30 AM'),
        (7, '7:00 AM'), (-8, '7:30 AM'),
        (8, '8:00 AM'), (-9, '8:30 AM'),
        (9, '9:00 AM'), (-10, '9:30 AM'),
        (10, '10:00 AM'), (-11, '10:30 AM'),
        (11, '11:00 AM'), (-12, '11:30 AM'),
        (12, '12:00 PM'), (-13, '0:30 PM'),
        (13, '1:00 PM'), (-14, '1:30 PM'),
        (14, '2:00 PM'), (-15, '2:30 PM'),
        (15, '3:00 PM'), (-16, '3:30 PM'),
        (16, '4:00 PM'), (-17, '4:30 PM'),
        (17, '5:00 PM'), (-18, '5:30 PM'),
        (18, '6:00 PM'), (-19, '6:30 PM'),
        (19, '7:00 PM'), (-20, '7:30 PM'),
        (20, '8:00 PM'), (-21, '8:30 PM'),
        (21, '9:00 PM'), (-22, '9:30 PM'),
        (22, '10:00 PM'), (-23, '10:30 PM'),
        (23, '11:00 PM'), (-24, '11:30 PM')], string='Hour to')
    # used only when the leave is taken in half days
    # used only when the leave is taken in half days
    request_date_from_period = fields.Selection([('am', 'Mañana'), ('pm', 'Tarde')],
        string="Fecha de inicio del período", default='am')
    # request type
    request_unit_half = fields.Boolean('Medio día')
    request_unit_hours = fields.Boolean('Horas personalizadas')
    request_unit_custom = fields.Boolean('Horas personalizadas de días')
    can_reset = fields.Boolean('Puede restablecer', compute='_compute_can_reset')
    can_approve = fields.Boolean('Puede aprobar', compute='_compute_can_approve')

    #Fechas

    number_of_days = fields.Float('Duracion (Dias)', copy=False, readonly=True, track_visibility='onchange',
                                    help='Number of days of the leave request according to your working schedule.')
    
    number_of_days_display = fields.Float('Duracion en dias', compute='_compute_number_of_days_display', copy=False, readonly=True,
                                            help='Number of days of the leave request. Used for interface.')
    
    number_of_hours_display = fields.Float('Duracion en horas', compute='_compute_number_of_hours_display', 
                                            copy=False, readonly=True)

    duration_display = fields.Char('Requested (Days/Hours)', compute='_compute_duration_display')    
    

    _sql_constraints = [
        ('date_check2', "CHECK ((date_from <= date_to))", "The start date must be anterior to the end date."),
        ('duration_check', "CHECK ( number_of_days >= 0 )", "If you want to change the number of days you should use the 'period' mode"),
    ]

    ops_ausencia_supervisor_id = fields.Many2one('hr.leave', string="Ausencias RRRHH", 
                                  ondelete='cascade', index=True)

    @api.onchange('holiday_status_id')
    @api.multi
    def _onchange_holiday_status_id(self):
        self.request_unit_half = False
        self.request_unit_hours = False
        self.request_unit_custom = False

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        domain = [('calendar_id', '=', self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].read_group(domain, ['ids:array_agg(id)', 'hour_from:min(hour_from)', 'hour_to:max(hour_to)', 'dayofweek', 'day_period'], ['dayofweek', 'day_period'], lazy=False)

        # Must be sorted by dayofweek ASC and day_period DESC
        attendances = sorted([DummyAttendance(group['hour_from'], group['hour_to'], group['dayofweek'], group['day_period']) for group in attendances], key=lambda att: (att.dayofweek, att.day_period != 'morning'))

        default_value = DummyAttendance(0, 0, 0, 'morning')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()), attendances[0] if attendances else default_value)
        # find last attendance coming before last_day
        attendance_to = next((att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()), attendances[-1] if attendances else default_value)

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif self.request_unit_hours:
            # This hack is related to the definition of the field, basically we convert
            # the negative integer into .5 floats
            hour_from = float_to_time(abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
            hour_to = float_to_time(abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'  # custom -> already in UTC
        self.date_from = timezone(tz).localize(datetime.combine(self.request_date_from, hour_from)).astimezone(UTC).replace(tzinfo=None)
        self.date_to = timezone(tz).localize(datetime.combine(self.request_date_to, hour_to)).astimezone(UTC).replace(tzinfo=None)
        self._onchange_leave_dates()

    @api.onchange('request_unit_half')
    def _onchange_request_unit_half(self):
        if self.request_unit_half:
            self.request_unit_hours = False
            self.request_unit_custom = False
        self._onchange_request_parameters()

    #Duracion en dias
    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_days_display(self):
        for holiday in self:
            holiday.number_of_days_display = holiday.number_of_days


    @api.multi
    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_reset(self):
        for holiday in self:
            try:
                holiday._check_approval_update('draft')
            except (AccessError, UserError):
                holiday.can_reset = False
            else:
                holiday.can_reset = True
    
    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        for holiday in self:
            try:
                if holiday.state == 'confirm' and holiday.holiday_status_id.validation_type == 'both':
                    holiday._check_approval_update('validate1')
                else:
                    holiday._check_approval_update('validate')
            except (AccessError, UserError):
                holiday.can_approve = False
            else:
                holiday.can_approve = True
    
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            return employee.get_work_days_data(date_from, date_to)['days']

        today_hours = self.env.user.company_id.resource_calendar_id.get_work_hours_count(
            datetime.combine(date_from.date(), time.min),
            datetime.combine(date_from.date(), time.max),
            False)

        return self.env.user.company_id.resource_calendar_id.get_work_hours_count(date_from, date_to) / (today_hours or HOURS_PER_DAY)



    #Duracion en horas
    @api.multi
    @api.depends('number_of_days')
    def _compute_number_of_hours_display(self):
        for holiday in self:
            calendar = holiday.employee_id.resource_calendar_id or self.env.user.company_id.resource_calendar_id
            if holiday.date_from and holiday.date_to:
                number_of_hours = calendar.get_work_hours_count(holiday.date_from, holiday.date_to)
                holiday.number_of_hours_display = number_of_hours or (holiday.number_of_days * HOURS_PER_DAY)
            else:
                holiday.number_of_hours_display = 0
    
    @api.multi
    @api.depends('number_of_hours_display', 'number_of_days_display')
    def _compute_duration_display(self):
        for leave in self:
            leave.duration_display = '%g %s' % (
                (float_round(leave.number_of_hours_display, precision_digits=2)
                if leave.leave_type_request_unit == 'hour'
                else float_round(leave.number_of_days_display, precision_digits=2)),
                _('hour(s)') if leave.leave_type_request_unit == 'hour' else _('day(s)'))

    @api.constrains('date_from', 'date_to')
    @api.multi
    def _check_date(self):
        for holiday in self:
            domain = [
                ('date_from', '<', holiday.date_to),
                ('date_to', '>', holiday.date_from),
                ('employee_id', '=', holiday.employee_id.id),
                ('id', '!=', holiday.id),
                ('state', 'not in', ['cancel', 'refuse']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_('You can not have 2 leaves that overlaps on the same day.'))

    @api.multi
    def _sync_employee_details(self):
        for holiday in self:
            holiday.manager_id = holiday.employee_id.parent_id.id
            if holiday.employee_id:
                holiday.department_id = holiday.employee_id.department_id

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self._sync_employee_details()
        self.holiday_status_id = False

    #CAMBIO DE FECHA A CERO
    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_leave_dates(self):    
        if self.date_from and self.date_to:
            self.number_of_days = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
        else:
            self.number_of_days = 0
    
    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('ops_supervisor_horas.asinhvien_giangvien_group')
        is_manager = self.env.user.has_group('ops_supervisor_horas.rrhh_giangvien_group')
        for holiday in self:
            val_type = holiday.holiday_status_id.validation_type
            
            if state == 'draft':
                continue

            if is_officer or is_manager:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')

          
    #Enviar aprobacion del supervisor 
    @api.multi
    def envio_aprobacion_supervisor(self):
        dia_Cal = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('La solicitud de permiso debe estar en estado Borrador ("Para enviar") para poder enviarla al supervisor.'))
        self.write({'state': 'confirm'})
        self.write({'number_of_days': dia_Cal})

        #self.activity_update()
        return True

    @api.multi
    def rechazar_aprobacion_supervisor(self):
        if self.filtered(lambda holiday: holiday.state != 'draft'):
            raise UserError(_('La solicitud de permiso debe estar en estado Borrador ("Para enviar") para poder enviarla al supervisor.'))
        self.write({'state': 'cancel'})
        #self.activity_update()
        return True
    
    #Enviar a RRHH --- Modulo ops enviar a modulo nomina 
    @api.multi
    def envio_aprobacion_rrhh(self):
        if self.filtered(lambda holiday: holiday.state != 'confirm'):
            raise UserError(_('La solicitud de permiso debe estar en estado  ("Enviado supervisor") para poder enviarla al depto de rrhh.'))
        #CAMBIA LA ETAPA A ENVIADO A RRHH
        self.write({'state': 'confirm2'})
        
        #CREA LA ASISTENCIA EN EL MODULO DE AUSENCIAS
        operaciones_crear = self.env['hr.leave']
        #today = date.today()
        #now = datetime.strftime(today, '%Y-%m-%d %H:%M:%S')
        dia_Cal = self._get_number_of_days(self.date_from, self.date_to, self.employee_id.id)
        project_line_vals = {
                    'state': 'confirm',
                    'ops_ausencia_leave_id': self.id,
                    'holiday_status_id':self.holiday_status_id.id,
                    'holiday_type': self.holiday_type,
                    'validation_type':self.validation_type,
                    'date_from':self.date_from,
                    'date_to': self.date_to,
                    'request_date_from': self.request_date_from,
                    'request_date_to': self.request_date_to,
                    'number_of_days': dia_Cal,
                    'number_of_hours_display': self.number_of_hours_display,
                    'number_of_days_display': self.number_of_days_display,
                    'employee_id': self.employee_id.id,
                    'user_id': self.user_id.id,
                    'name': self.name
                    }
        res = operaciones_crear.create(project_line_vals)
        
        #Crea la asitencia luego la relacion con este modulo
        self.write({'ops_ausencia_supervisor_id': res.id})
        #cambio los dias del modulo
        self.write({'number_of_days': dia_Cal})
        self.env.user.notify_success(message='Se envio correctamente a RRHH.')
        #self.activity_update()
        return True


