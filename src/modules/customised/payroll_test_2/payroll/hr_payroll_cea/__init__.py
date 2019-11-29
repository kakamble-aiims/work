from trytond.pool import Pool
from .hr_payroll_cea import *


def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_cea', type_='model')
