from trytond.pool import Pool
from .hr_hda import *


def register():
    Pool.register(
        HighDegreeAllowance,
        module='hr_hda', type_='model')