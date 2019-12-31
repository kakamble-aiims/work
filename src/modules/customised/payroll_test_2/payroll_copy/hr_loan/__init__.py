# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .computer_loan import *
from .hba_loan import *
from .hba_report import *


def register():
    Pool.register(
        ComputerLoan,
        LoanCancelreason,
        ComputerloanLine,
        HouseBuildingLoan,
        Construction,
        OwnHouse,
        HBAloanLine,
        HBASchedule,
        ComputerLoanSchedule,
        module='hr_loan', type_='model')
    Pool.register(
        HBAScheduleWiz,
        ComputerLoanScheduleWiz,
        module='hr_loan', type_='wizard')
    Pool.register(
        HBAReport,
        ComputerLoanReport,
        module='hr_loan', type_='report')
