from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow
import datetime
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, PYSONEncoder
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button

__all__ = [
    'ChildernEductionAllowance', 'ChildrenEmployee', 'ChildrenEmployeeList',
    'ChildrenEduactionAllowanceWiz', 'ChildrenList'
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
    from_date = fields.Date('From Date', states={
        'readonly': ~Eval('state').in_(['draft'])
    },
        depends=['state'])
    to_date = fields.Date('To Date', states={
        'readonly': ~Eval('state').in_(['draft'])
    },
        depends=['state'])
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

    @staticmethod
    def default_from_date():
        return datetime.date.today()

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
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None

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


class ChildrenEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('children.list', 'Employee List')


class ChildrenEmployeeList(ModelView):
    'Children Eduaction Employee List'

    __name__ = 'children.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many(
        'children.list', 'childrenemployee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class ChildrenList(ModelSQL, ModelView):
    'Children Employee List'

    __name__ = 'children.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    childrenemployee_list = fields.Many2One(
        'children.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class ChildrenEduactionAllowanceWiz(Wizard):
    'Children Eduaction Allowance Wizard'

    __name__ = 'children.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'children.employee.list',
        'hr_cea.form_wiz_children_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_cea_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_cea_form = StateTransition()
    open_ = StateAction('hr_cea.action_cea')

    def transition_create_cea_form(self):
        pool = Pool()
        vals = {}
        create_cea_form = []
        cea = pool.get('hr.allowance.cea')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_cea_form.append(cea.create([vals]))
        self.raises.cea_form = create_cea_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
