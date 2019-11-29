from trytond.pool import Pool
from .hr_payroll_exam_section import *

def register():
    Pool.register(
        HrSalaryRule,
        module='hr_payroll_exam_section', type_='model')
