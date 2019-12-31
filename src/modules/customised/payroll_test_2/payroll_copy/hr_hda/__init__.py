from trytond.pool import Pool
from .hr_hda import *


def register():
    Pool.register(
        HighDegreeAllowance,
        HdaEmployeeList,
        HdaEmployee,
        HdaList,
        module='hr_hda', type_='model')

    Pool.register(
        HighDegreeAllowanceWiz,
        module='hr_hda', type_='wizard')
