from trytond.pool import Pool
from .hr_icu import *

def register():
    Pool.register(
        ICUAllowance,
        module='hr_icu', type_='model')