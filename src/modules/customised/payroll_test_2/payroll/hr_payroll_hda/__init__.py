from trytond.pool import Pool
from .hr_payroll_hda import *


def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_hda', type_='model')
