from trytond.pool import Pool
from .hr_hra import *


def register():
    Pool.register(
       HouseRentAllowance,
       module='hr_hra', type_='model')