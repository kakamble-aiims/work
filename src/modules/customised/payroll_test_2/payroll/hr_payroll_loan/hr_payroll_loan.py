from trytond.pool import Pool, PoolMeta
from datetime import datetime, date
from trytond.model import (
    ModelView, ModelSQL, fields, Workflow)

__all__ = ['SalaryRule', 'HrPayslip']


class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_COM_Loan(self, payslip, employee, contract):
        ''' Calcualte this method for computer loan'''
        pool = Pool()
        amount = 0
        computerloan = pool.get('computer.loan')
        computer_loan = computerloan.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        print(computer_loan, "computer_loan")
        if computer_loan:
            for loan in computer_loan:
                mydate = datetime.now().month
                months = date(1900, mydate, 1).strftime('%B')
                loan_line = pool.get('computer.loan.line')
                loan_lines = loan_line.search([
                    ('loan', '=', loan.id),
                    ('status', '=', 'pending'),
                    ('month', '=', months)])
                if loan_lines:
                    loan_lines[0].status = 'inprogress'
                    loan_lines[0].save()
                    amount += loan_lines[0].amount
        return amount

    def calculate_HBA_Loan(self, payslip, employee, contract):
        ''' Calcualte this method for HBA Loan'''
        pool = Pool()
        HBALoan = pool.get('hba.loan')
        hba_loan = HBALoan.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        amount = 0
        if hba_loan:
            for loan in hba_loan:
                mydate = datetime.now().month
                months = date(1900, mydate, 1).strftime('%B')
                loan_line = pool.get('hba.loan.line')
                loan_lines = loan_line.search([
                    ('loan', '=', loan.id),
                    ('status', '=', 'pending'),
                    ('month', '=', months)])
                if loan_lines:
                    loan_lines[0].status = 'inprogress'
                    loan_lines[0].save()
                    amount += loan_lines[0].amount
        return amount


class HrPayslip(metaclass=PoolMeta):

    __name__ = 'hr.payslip'

    @classmethod
    @ModelView.button
    @Workflow.transition('paid')
    def done(cls, records):
        for record in records:
            pool = Pool()
            computerloan = pool.get('computer.loan')
            computerloans = computerloan.search([
                ('employee', '=', record.employee),
                ('salary_code', '=', record.employee.salary_code),
                ('state', '=', 'approve')
            ])
            if computerloans:
                amount = 0
                for com_loan in computerloans:
                    computerloan_line = pool.get('computer.loan.line')
                    computerloan_lines = computerloan_line.search([
                            ('loan', '=', com_loan.id),
                            ('status', '=', 'inprogress')])
                    if computerloan_lines:
                        computerloan_lines[0].status = 'done'
                        computerloan_lines[0].save()
            hbaloan = pool.get('hba.loan')
            hbaloans = hbaloan.search([
                ('employee', '=', record.employee),
                ('salary_code', '=', record.employee.salary_code),
                ('state', '=', 'approve')
            ])
            if hbaloans:
                amount = 0
                for hba_loan in hbaloans:
                    hbaloan_line = pool.get('hba.loan.line')
                    hbaloan_lines = hbaloan_line.search([
                            ('loan', '=', hba_loan.id),
                            ('status', '=', 'inprogress')])
                    if hbaloan_lines:
                        hbaloan_lines[0].status = 'done'
                        hbaloan_lines[0].save()
        pass
