from trytond.pool import Pool
from .hr_payroll_bills import *


def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_bills', type_='model')
