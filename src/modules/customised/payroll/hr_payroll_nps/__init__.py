from trytond.pool import Pool
from .hr_payroll_nps import *


def register():
    Pool.register(
        SalaryRule,
        module='hr_payroll_nps', type_='model')