from trytond.pool import Pool
from .hr_ota import *


def register():
    Pool.register(
        OverTimeAllowance,
        OtaEmployeeList,
        OtEmployee,
        OtaList,
        module='hr_ota', type_='model')

    Pool.register(
        OverTimeAllowanceWiz,
        module='hr_ota', type_='wizard')
