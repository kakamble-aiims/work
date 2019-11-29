from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
import datetime

__all__ = ['SalaryRule']


class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'


    #Computer Loan
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
                mydate = datetime.datetime.now().month
                months = datetime.date(1900, mydate, 1).strftime('%B')
                loan_line = pool.get('computer.loan.line')
                print(months, "Monthss")
                loan_lines = loan_line.search([
                    ('loan', '=', loan.id),
                    ('status', '=', 'pending'),
                    ('month', '=', months)])
                amount += loan_lines[0].amount
            return amount
        else:
            return 0

    # HBA Loan
    def calculate_HBA_Loan(self, payslip, employee, contract):
        ''' Calcualte this method for HBA Loan'''
        pool = Pool()
        hbacomputerloan = pool.get('hba.loan')
        hba_loan = hbaloan.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        if hba_loan:
            amount = 0
            for loan in hba_loan:
                mydate = datetime.datetime.now().month
                months = datetime.date(1900, mydate, 1).strftime('%B')
                loan_line = pool.get('hba.loan.line')
                print(months, "Monthss")
                loan_lines = loan_line.search([
                    ('loan', '=', loan.id),
                    ('status', '=', 'pending'),
                    ('month', '=', months)])
                amount += loan_lines[0].amount
            return amount
        else:
            return 0