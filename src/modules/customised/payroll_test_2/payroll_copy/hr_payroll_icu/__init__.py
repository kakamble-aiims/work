from trytond.pool import Pool
from .hr_payroll_icu import *

def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_icu', type_='model')