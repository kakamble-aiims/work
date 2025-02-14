# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .loan import *

def register():
    Pool.register(
        ComputerLoan,
        LoanCancelreason,
        loanLine,
        module='loan', type_='model')
