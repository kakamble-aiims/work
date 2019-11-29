from trytond.pool import Pool
from .hr_bills import *


def register():
    Pool.register(
        NewspaperAllowance, 
        TelephoneAllowance,
        module='hr_bills', type_='model')