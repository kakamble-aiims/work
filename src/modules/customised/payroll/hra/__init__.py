from trytond.pool import Pool
from .hra import *


def register():
    Pool.register(
        HRA_Allowance,
        module='hra', type_='model')