from trytond.pool import Pool
from .hr_conveyance import *

def register():
    Pool.register(
        Conveyance_Allowance,
        module='hr_conveyance', type_='model')
