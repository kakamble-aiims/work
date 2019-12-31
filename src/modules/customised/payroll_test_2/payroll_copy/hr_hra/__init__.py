from trytond.pool import Pool
from .hr_hra import *


def register():
    Pool.register(
       HouseRentAllowance,
       HraEmployeeList,
       HrEmployee,
       HraList,
       module='hr_hra', type_='model')
    Pool.register(
       HouseRentAllowanceWiz,
       module='hr_hra', type_='wizard')
