from trytond.pool import Pool
from .hr_cea import *

def register():
    Pool.register(
        ChildernEductionAllowance,
        module='hr_cea', type_='model')