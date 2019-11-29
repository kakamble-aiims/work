from trytond.pool import Pool
from .hr_ota import *

def register():
    Pool.register(
        OverTimeAllowance,
        module='hr_ota', type_='model')