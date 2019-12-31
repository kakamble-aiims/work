from trytond.pool import Pool
from .hr_payroll_estate import *


def register():
    Pool.register(
        SalaryRule,
        module='hr_payroll_estate', type_='model')
