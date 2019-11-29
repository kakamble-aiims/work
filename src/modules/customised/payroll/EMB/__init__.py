from trytond.pool import Pool
from .emb import *

def register():
    Pool.register(
        EMBEmployeeDetails,
        EMB,
        module='emb', type_='model')
