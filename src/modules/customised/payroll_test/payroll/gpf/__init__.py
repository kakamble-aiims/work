# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .gpf_change import *
from .gpf_advance import *

def register():
    Pool.register(
        GPFSubscription,
        HrContract,
        HrEmployee,
        GPFAdvance,
        GPFreason,
        GPFCancelreason,
        GPFAdvanceLine,
        module='gpf', type_='model')
