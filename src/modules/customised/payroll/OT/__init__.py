from trytond.pool import Pool
from .ot import *


def register():
    Pool.register(
        OTEmployeeDetails, OTEmployeeLog,
        module='ot', type_='model')

