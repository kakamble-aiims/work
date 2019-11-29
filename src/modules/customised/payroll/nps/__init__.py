from trytond.pool import Pool
from .nps import *


def register():
    Pool.register(
        NpsDetails,
        Ddo,
        HrEmployee,
        NpsLine,
        module='nps', type_='model')