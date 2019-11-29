from trytond.pool import Pool
from .hr_bank import *


def register():
    Pool.register(
        BankDetails,
        HrEmployee,
        module='hr_bank', type_='model')
