from trytond.pool import Pool
from .hr_emb import *


def register():
    Pool.register(
        EMBEmployeeDetails,
        EMB,
        module='hr_emb', type_='model')
