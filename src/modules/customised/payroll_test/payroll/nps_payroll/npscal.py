import datetime
from trytond.pool import Pool, PoolMeta

__all__ = [
    'SalaryRule',
    ]

class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_NPS(self, payslip, employee, contract):
        doj = datetime.date(2003, 12, 31)
        if employee.date_of_joining>doj:
            nps = (0.1 * contract.basic)
            return nps
        return None
