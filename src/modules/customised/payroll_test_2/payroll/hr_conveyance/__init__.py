from trytond.pool import Pool
from .hr_conveyance import *


def register():
    Pool.register(
        Conveyance_Allowance,
        ConveyanceEmployeeList,
        ConveyanceEmployee,
        ConveyanceList,
        module='hr_conveyance', type_='model')

    Pool.register(
        ConveyanceAllowanceWiz,
        module='hr_conveyance', type_='wizard')
