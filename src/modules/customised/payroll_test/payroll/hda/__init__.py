from trytond.pool import Pool
from .hda import *


def register():
    Pool.register(
        HighDegreeAllowance,
        module='hda', type_='model')