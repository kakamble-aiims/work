from trytond.pool import Pool
from .loan_advance import *


def register():
    Pool.register(
        AdvanceApplication,
        ApplicationSignature,
        module='loan_advance', type_='model'
    )