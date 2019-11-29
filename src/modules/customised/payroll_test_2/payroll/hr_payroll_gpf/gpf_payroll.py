from trytond.pool import Pool, PoolMeta
from trytond.model import (ModelSQL, ModelView, fields, Workflow)

__all__ = ['SalaryRule', 'HrPayslip']


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
            ('state', '=', 'approve'),
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
                gpf_advance_line[0].status = 'inprogress'
                gpf_advance_line[0].save()
            return amount
        return 0


class HrPayslip(metaclass=PoolMeta):

    __name__ = 'hr.payslip'

    @classmethod
    @ModelView.button
    @Workflow.transition('paid')
    def done(cls, records):
        for record in records:
            if record.employee.gpf_nps == 'gpf':
                pool = Pool()
                gpfadvance = pool.get('gpf.advance')
                gpf_advance = gpfadvance.search([
                    ('employee', '=', record.employee),
                    ('salary_code', '=', record.employee.salary_code),
                    ('state', '=', 'approve'),
                    ('refund', '=', 'refundable')
                ])
                if gpf_advance:
                    amount = 0
                    for gpf_rec in gpf_advance:
                        gpfadvance_line = pool.get('gpf.advance.line')
                        gpf_advance_line = gpfadvance_line.search([
                            ('gpf_advance', '=', gpf_rec.id),
                            ('status', '=', 'inprogress')])
                        amount += gpf_advance_line[0].amount
                        gpf_advance_line[0].status = 'done'
                        gpf_advance_line[0].save()
        pass