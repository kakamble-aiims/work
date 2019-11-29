from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta 
from datetime import *
import requests
import random
from trytond.transaction import Transaction


__all__ = [
    'NewspaperAllowance' , 'TelephoneAllowance'
    ]


class NewspaperAllowance(ModelSQL, ModelView):
    'Employee Newspaper Bill Allowance'

    __name__ = 'newspaper.bill'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    month = fields.Char('Month')
    bill_amount = fields.Float('Bill Claim Amount')
    bill_attachment = fields.Char('Bill Attachment')

    @staticmethod
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None
    
   
    @classmethod
    def default_month(cls):
        prev = date.today().replace(day=1) - timedelta(days=1)
        return (prev.strftime("%B"))

    @fields.depends('employee')
    def on_change_employee(self):
        self.salary_code=self.employee.salary_code   


class TelephoneAllowance(ModelSQL, ModelView):
    'Employee Telephone Bill Allowance'

    __name__ = 'telephone.bill'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    month = fields.Char('Month')
    bill_claim_amount = fields.Float('Bill Claim Amount')
    bill_attachment = fields.Char('Bill Attachment')
    
    
    @classmethod
    def default_month(cls):
        prev = date.today().replace(day=1) - timedelta(days=1)
        return (prev.strftime("%B"))
    
    @fields.depends('employee')
    def on_change_employee(self):
        self.salary_code=self.employee.salary_code
    
    