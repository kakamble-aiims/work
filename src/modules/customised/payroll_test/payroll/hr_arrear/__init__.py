from trytond.pool import Pool
from .hr_arrear import *

def register():
    Pool.register(
        HR_Arrear,
        module='hr_arrear', type_='model')
