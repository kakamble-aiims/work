from trytond.pool import Pool

from .employee import *


def register():
    Pool.register(
        Department,
        CompanyEmployeeGrade,
        HrEmployee,
        EmployeeDesignation,
        EmployeePosting,
        GradePay,
        Party,
        EmployeeDependents,
        Leave,
        Bank,
        BankAccounts,
        module='hr', type_='model')
