from trytond.pool import Pool
from .hr_payroll_nps import *

def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_nps', type_='model')