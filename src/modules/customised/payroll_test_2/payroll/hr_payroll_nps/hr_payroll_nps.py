import datetime
from trytond.pool import PoolMeta

__all__ = [
    'HrSalaryRule',
]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_NPS(self, payslip, employee, contract):
        amount = 0
        doj = datetime.date(2003, 12, 31)
        if employee.date_of_joining > doj:
            amount = (0.1 * contract.basic)
        return amount
