from trytond.pool import Pool
from .hda import *


def register():
    Pool.register(
        HDA_Allowance,
        module='hda', type_='model')