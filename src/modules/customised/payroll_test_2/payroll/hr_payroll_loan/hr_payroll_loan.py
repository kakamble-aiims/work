from trytond.pool import Pool, PoolMeta
from datetime import datetime, date

__all__ = ['SalaryRule']


class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_COM_Loan(self, payslip, employee, contract):
        ''' Calcualte this method for computer loan'''
        pool = Pool()
        computerloan = pool.get('computer.loan')
        computer_loan = computerloan.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        if computer_loan:
            amount = 0
            for loan in computer_loan:
                mydate = datetime.now().month
                months = date(1900, mydate, 1).strftime('%B')
                loan_line = pool.get('computer.loan.line')
                loan_lines = loan_line.search([
                    ('loan', '=', loan.id),
                    ('status', '=', 'pending'),
                    ('month', '=', months)])
                amount += loan_lines[0].amount
            return amount
        else:
            return 0

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
                amount += loan_lines[0].amount
        return amount
