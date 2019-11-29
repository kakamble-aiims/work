from trytond.pool import Pool
from .hra import *


def register():
    Pool.register(
       HouseRentAllowance,
        module='hra', type_='model')