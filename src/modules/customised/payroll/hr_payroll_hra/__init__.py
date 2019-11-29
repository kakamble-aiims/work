from trytond.pool import Pool
from .hr_payroll_hra import *

def register():
    Pool.register(
        SalaryRule,
        module='hr_payroll_hra', type_='model')