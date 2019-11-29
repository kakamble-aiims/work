from trytond.pool import Pool
from .conveyance import *


def register():
    Pool.register(
       Conveyance_Allowance,
        module='conveyance', type_='model')