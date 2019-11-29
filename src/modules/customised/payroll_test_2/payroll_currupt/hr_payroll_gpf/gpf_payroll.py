from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval

__all__ = ['SalaryRule']


class SalaryRule(metaclass=PoolMeta):
    'Salary Rule'

    __name__ = 'hr.salary.rule'


    def calculate_GPF(self, payslip, employee, contract):
        if contract.gpf_amount:
            return contract.gpf_amount

    def calculate_GPFR(self, payslip, employee, contract):
        pool = Pool()
        gpfadvance = pool.get('gpf.advance')
        gpf_advance = gpfadvance.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            #('state', '=', 'approve')
            ('refund', '=', 'refundable')
            ])
        if gpf_advance:
            amount = 0
            for gpf_rec in gpf_advance:
                gpfadvance_line = pool.get('gpf.advance.line')
                gpf_advance_line = gpfadvance_line.search([
                    ('gpf_advance', '=', gpf_rec.id),
                    ('status', '=', 'pending')])
                amount += gpf_advance_line[0].amount
            return amount
        else:
            return 0
