from trytond.pool import Pool
from .hr_cash import *


def register():
    Pool.register(
        CashAllowance,
        CashEmployeeList,
        CashEmployee,
        CashList,
        module='hr_cash', type_='model')

    Pool.register(
        CashHandlingAllowanceWiz,
        module='hr_cash', type_='wizard')
