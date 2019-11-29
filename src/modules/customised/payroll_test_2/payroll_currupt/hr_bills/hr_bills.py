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
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    bill_amount = fields.Float('Bill Claim Amount')
    bill_attachment = fields.Char('Bill Attachment')

    
   
    # @classmethod
    # def default_month(cls):
    #     prev = date.today().replace(day=1) - timedelta(days=1)
    #     return (prev.strftime("%B"))

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department

    @staticmethod
    def default_employee():
        global current_employee
        current_employee = None
        pool = Pool()
        Employee = pool.get('company.employee')
        employee_id = Transaction().context.get('employee')
        employee = Employee.search([
            ('id', '=', employee_id)
        ])
        if employee != []:
            current_employee = employee[0]
        return current_employee.id if current_employee else None
        
class TelephoneAllowance(ModelSQL, ModelView):
    'Employee Telephone Bill Allowance'

    __name__ = 'telephone.bill'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    bill_claim_amount = fields.Float('Bill Claim Amount')
    bill_attachment = fields.Char('Bill Attachment')
    
    
    # @classmethod
    # def default_month(cls):
    #     prev = date.today().replace(day=1) - timedelta(days=1)
    #     return (prev.strftime("%B"))
    
    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department
  
    @staticmethod
    def default_employee():
        global current_employee
        current_employee = None
        pool = Pool()
        Employee = pool.get('company.employee')
        employee_id = Transaction().context.get('employee')
        employee = Employee.search([
            ('id', '=', employee_id)
        ])
        if employee != []:
            current_employee = employee[0]
        return current_employee.id if current_employee else None
    
    