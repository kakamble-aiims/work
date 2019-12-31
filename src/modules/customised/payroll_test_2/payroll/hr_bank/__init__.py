from trytond.pool import Pool
from .hr_bank import *
from .bank_report import *


def register():
    Pool.register(
        BankDetails,
        HrEmployee,
        BankStatementSchedule,
        module='hr_bank', type_='model')
    Pool.register(
        BankStatementScheduleWiz,
        module='hr_bank', type_='wizard')
    Pool.register(
        BankStatementReport,
        module='hr_bank', type_='report')
