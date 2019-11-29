from trytond.pool import Pool
from .hr_bills import *


def register():
    Pool.register(
        NewspaperAllowance,
        NewspaperEmployeeList,
        NewspaperEmployee,
        NewspaperList,
        TelephoneAllowance,
        TelephoneEmployeeList,
        TelephoneEmployee,
        TelephoneList,
        module='hr_bills', type_='model')
    Pool.register(
        NewspaperAllowanceWiz,
        TelephoneAllowanceWiz,
        module='hr_bills', type_='wizard')
