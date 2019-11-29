from trytond.pool import Pool
from .hr_estate import *


def register():
    Pool.register(
        EstateAllotment,
        QuarterType,
        QuarterTypeLocation,
        module="hr_estate", type_="model")
