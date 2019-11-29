from trytond.pool import Pool
from .bills import *


def register():
    Pool.register(
        NewspaperAllowance, 
        TelephoneAllowance,
        module='bills', type_='model')