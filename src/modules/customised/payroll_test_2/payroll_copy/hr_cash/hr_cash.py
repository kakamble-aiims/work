from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.pool import Pool
from trytond.pyson import Eval
import datetime
from trytond.transaction import Transaction

__all__ = [
    'CashAllowance',
    ]


class CashAllowance(Workflow, ModelSQL, ModelView):
    """Cash Handling and Treasury Allowance for an Employee"""

    __name__ = 'hr.allowance.cash'

    _STATES = {
        'readonly': ~Eval('state').in_(['draft'])
    }

    _DEPENDS = ['state']
    
    salary_code = fields.Char('Salary Code', states=_STATES,
        depends=_DEPENDS
    )
    employee = fields.Many2One('company.employee', 'Employee Name',
        states=_STATES, depends=_DEPENDS
    )
    designation = fields.Many2One('employee.designation', 'Designation',
        states=_STATES, depends=_DEPENDS
    )
    department = fields.Many2One('company.department', 'Department',
        states=_STATES, depends=_DEPENDS
    )
    amount = fields.Integer('Amount',
        states=_STATES, depends=_DEPENDS
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('cash_section_officer', 'Cash Section_officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
        ], 'Status', readonly=True)

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department

    @staticmethod
    def default_state():
        return 'draft'


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

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'submit': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'send_for_cash_section_officer_approval': {
                'invisible': ~Eval('state').in_(['submit'])
            },
            'approve': {
                'invisible': ~Eval('state').in_(['cash_section_officer'])
            },
            'cancel': {
                'invisible': Eval('state').in_(['draft', 'approve', 'cancel'])
            },
        })
        cls._transitions |= set((
            ('draft', 'submit'),
            ('submit', 'cash_section_officer'),
            ('submit', 'cancel'),
            ('cash_section_officer', 'approve'),
            ('cash_section_officer', 'cancel'),
        ))

    @classmethod
    @Workflow.transition('submit')
    def submit(cls, records):
        pass

    @classmethod
    @Workflow.transition('cash_section_officer')
    def send_for_cash_section_officer_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('approve')
    def approve(cls, records):
        pass

    @classmethod
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass