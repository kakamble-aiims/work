from trytond.pool import Pool
from .hr_icu import *


def register():
    Pool.register(
        ICUAllowance,
        IcuEmployeeList,
        IcuEmployee,
        IcuList,
        module='hr_icu', type_='model')

    Pool.register(
        ICUAllowanceWiz,
        module='hr_icu', type_='wizard')
