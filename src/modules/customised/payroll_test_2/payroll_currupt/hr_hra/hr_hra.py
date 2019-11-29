from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.model import Workflow
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'HouseRentAllowance',
    ]


class HouseRentAllowance(Workflow, ModelSQL, ModelView):
    """House Rent Allowance for an Employee"""

    __name__ = 'hr.allowance.hra'


    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    designation = fields.Many2One('company.employee','Designation')
    department = fields.Many2One('company.employee','Department')
    date = fields.Date('Date', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    address = fields.Char('House Address', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    rent = fields.Float('Expenditure On Rent', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('submit', 'Submit'),
            ('cash_section_officer', 'Cash Section_officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
            
        ], 'Status', readonly=True)
    # date = fields.Date('Date')
    # address = fields.Char('House Address')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "submit": {
                'invisible': ~Eval('state').in_(
                    ['draft', 'confirm'
                     ]),
            },
            
            "cancel": {
                'invisible': ~Eval('state').in_(
                    ['cash_section_officer'
                     ]),
            },


            "approve": {
                'invisible': ~Eval('state').in_(
                    ['cash_section_officer'
                     ]),
                
            },     
        })
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('confirm', 'submit'),
            ('submit', 'cash_section_officer'),
            ('cash_section_officer', 'approve'),
            ('cash_section_officer', 'cancel'),
            ))
            
    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cash_section_officer')
    def submit(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approve')
    def approve(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass

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