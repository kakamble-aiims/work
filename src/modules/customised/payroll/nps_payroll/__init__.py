from trytond.pool import Pool
from .npscal import *


def register():
    Pool.register(
        SalaryRule,
        module='nps_payroll', type_='model')