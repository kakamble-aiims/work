from trytond.pool import Pool
from .hr_payroll_ota import *

def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_ota', type_='model')