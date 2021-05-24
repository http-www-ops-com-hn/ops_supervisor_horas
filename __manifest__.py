# -*- coding: utf-8 -*-
{
    'name': "Agregar Horas Extras (Supervisor)",
    'summary': """
        Este modulo sirve para que el supervisor agregue horas extras, deducciones a sus suburdinados, luego el departamento de RRHH las aprueba.
        """,
    'author': "Ariel Cerrato",
    'website': "https://www.bintell.net/",
    'category': 'payroll',
    'version': '1.0',
    'license': 'OPL-1',
    'data': [
        'security/group_horas_supervisor.xml',
        'security/ir.model.access.csv',
        'views/add_horas_supervisor.xml',
        'views/add_horas_precio.xml',
        'views/add_deducciones.xml',
        'views/add_ingresos.xml',
        'views/proyecto_tipo.xml',
        'views/cartera_tipo.xml',
        'views/add_configuraciones.xml',
        'views/add_dedu_ingre.xml',
        'views/add_solicitud_ausencia.xml',
        'views/inherint_asuencia.xml',
        'views/inherint_employee.xml',
        'views/subproyecto.xml',
        'views/estimado_comisiones.xml',
        
       
    ],
    'depends': ['hr','hr_payroll','hr_attendance'],
    'installable': True,
    'auto_install': False,
    'application': True,
}