from trytond.pool import Pool
from .hr_payroll_hra import *


def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_hra', type_='model')
