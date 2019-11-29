from trytond.pool import Pool
from .hr_cash import *

def register():
    Pool.register(
        CashAllowance,
        module='hr_cash', type_='model')