from trytond.pool import Pool
from .lra import *


def register():
    Pool.register(
        LR_Allowance,
        module='lra', type_='model')
