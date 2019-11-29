from trytond.pool import Pool
from .estate import *

def register():
    Pool.register(
        EstateAllotment,
        QuarterType,
        QuarterTypeLocation,
        module="estate", type_="model"
    )