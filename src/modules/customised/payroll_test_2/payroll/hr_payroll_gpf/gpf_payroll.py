from trytond.pool import Pool, PoolMeta
from trytond.model import (ModelSQL, ModelView, fields, Workflow)
from datetime import datetime

__all__ = ['SalaryRule', 'HrPayslip']


class SalaryRule(metaclass=PoolMeta):
    'Salary Rule'

    __name__ = 'hr.salary.rule'

    def calculate_GPF(self, payslip, employee, contract):
        amount = 0
        if employee.gpf_nps == 'gpf' and contract.gpf_amount:
            amount =  contract.gpf_amount
        return amount

    def calculate_GPFR(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        gpfadvance = pool.get('gpf.advance')
        gpf_advance = gpfadvance.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve'),
            ('refund', '=', 'refundable')
        ])
        if gpf_advance:
            for gpf_rec in gpf_advance:
                gpfadvance_line = pool.get('gpf.advance.line')
                gpf_advance_line = gpfadvance_line.search([
                    ('gpf_advance', '=', gpf_rec.id),
                    ('status', '=', 'pending')])
                if gpf_advance_line:
                    amount += gpf_advance_line[0].amount
                    gpf_advance_line[0].status = 'inprogress'
                    gpf_advance_line[0].save()
        return amount


class HrPayslip(metaclass=PoolMeta):

    __name__ = 'hr.payslip'

    @classmethod
    @ModelView.button
    @Workflow.transition('paid')
    def done(cls, records):
        for record in records:
            gpf_balance = 0
            if record.employee.gpf_nps == 'gpf':
                pool = Pool()
                gpfadvance = pool.get('gpf.advance')
                employee = pool.get('company.employee')
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
                        if gpf_advance_line:
                            amount += gpf_advance_line[0].amount
                            gpf_advance_line[0].status = 'done'
                            gpf_advance_line[0].save()
                            gpf_balance = record.employee.gpf_balance + amount + record.contract.gpf_amount
                            vals = {
                                'amount': amount,
                                'date' : datetime.now().date(),
                                'description' : 'ABCCCCCCCDDDD',
                                'gpf_type' : 'deposit_loan',
                                'gpf_lines' : record.employee
                            }
                            gpf_lines_data.create([vals])

                else:
                    gpf_balance = record.employee.gpf_balance + record.contract.gpf_amount
                employee.write([record.employee], {
                    'gpf_balance': (gpf_balance),
                    })
                
                gpf_lines_data = pool.get('hr.gpf.lines')
                vals = {
                    'amount': record.contract.gpf_amount,
                    'date' : datetime.now().date(),
                    'description' : 'ABCCCCCCCDDDD',
                    'gpf_type' : 'deposit_subscribe',
                    'gpf_lines' : record.employee
                }
                gpf_lines_data.create([vals])

        pass
