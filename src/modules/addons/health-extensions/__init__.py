from trytond.pool import Pool

from .health import *


def register():
    Pool.register(
        Establishment,
        Department,
        module='aiims_health_extn', type_='model')
