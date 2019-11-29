from trytond.pool import Pool
from .hr_arrear import *


def register():
    Pool.register(
        HrPayslipLines,
        HRArrear,
        HrDrawn, 
        module='hr_arrear', type_='model')
