from trytond.pool import Pool
from .hr_cea import *


def register():
    Pool.register(
        ChildernEductionAllowance,
        ChildrenEmployeeList,
        ChildrenEmployee,
        ChildrenList,
        module='hr_cea', type_='model')

    Pool.register(
        ChildrenEduactionAllowanceWiz,
        module='hr_cea', type_='wizard')
