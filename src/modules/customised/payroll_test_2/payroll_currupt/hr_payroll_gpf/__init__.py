# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .gpf_payroll import *

def register():
    Pool.register(
        SalaryRule,
        module='hr_payroll_gpf', type_='model')
