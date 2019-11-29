from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool
from trytond.model import Workflow
from trytond.pyson import Eval
import datetime
from trytond.transaction import Transaction

__all__ = [
    'ChildernEductionAllowance',
    ]


class ChildernEductionAllowance(Workflow, ModelSQL, ModelView):
    """Childern Eduction Allowance for an Employee"""

    __name__ = 'hr.allowance.cea'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee Name')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    children_no = fields.Selection(
        [
            ('1', 'One'),
            ('2', 'Two'),
        ], 'Number of Children')
               
    amount = fields.Function(
        fields.Float('Education Amount'),
        'on_change_with_amount'
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('cash_section_officer', 'Cash Section_officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
        ], 'Status', readonly=True)

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'submit': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'cash_section_officer_approval': {
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
    def cash_section_officer_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('approve')
    def approve(cls, records):
        pass

    @classmethod
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
    def default_state():
        return 'draft'

    # @classmethod
    # def validate(cls, records):
    #     super(ChildernEductionAllowance ,cls).validate(records)
    #     for record in records:
    #         record.check_children_no()

    # def check_children_no(self):
    #     'Check number of children'
        # if self.children_no:
        #     if(self.children_no == '1'):
        #         if self.amount != 2250:
        #             self.raise_user_error('amount is worng')
        #     elif(self.children_no == '2'):
        #         if self.amount != 4500:
        #             self.raise_user_error('amount is worng')

    @fields.depends('children_no')
    def on_change_with_amount(self, name=None):
        res = 0
        if self.children_no:
            if(self.children_no == '1'):
                res = 2250
            elif(self.children_no == '2'):
                res = 4500
        return res


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
    