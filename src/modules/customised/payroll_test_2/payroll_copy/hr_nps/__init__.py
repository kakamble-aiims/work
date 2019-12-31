from trytond.pool import Pool
from .hr_nps import *


def register():
    Pool.register(
        NpsDetails,
        Ddo,
        HrEmployee,
        NpsLine,
        module='hr_nps', type_='model')
