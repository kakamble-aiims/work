from trytond.pool import Pool
from .hr_payroll_arrear import *


def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_arrear', type_='model')
