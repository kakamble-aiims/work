from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.model import Workflow
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, PYSONEncoder
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button

__all__ = [
    'HouseRentAllowance', 'HraEmployeeList', 'HrEmployee',
    'HouseRentAllowanceWiz', 'HraList'
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
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    from_date = fields.Date('From Date', states={
        'readonly': ~Eval('state').in_(['draft'])
    },
        depends=['state'])
    to_date = fields.Date('To Date', states={
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

    @staticmethod
    def default_from_date():
        return datetime.date.today()

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
    @ModelView.button_action('submit')
    def submit(cls, records):
        pass

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
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None

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


class HrEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('hra.list', 'Employee List')


class HraEmployeeList(ModelView):
    'HRA Employee List'

    __name__ = 'hra.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many('hra.list', 'hremployee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class HraList(ModelSQL, ModelView):
    'HRA List'

    __name__ = 'hra.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    hremployee_list = fields.Many2One('hra.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class HouseRentAllowanceWiz(Wizard):
    'House Rent Allowance Wizard'

    __name__ = 'hra.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'hra.employee.list',
        'hr_hra.form_wiz_hra_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_hra_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_hra_form = StateTransition()
    open_ = StateAction('hr_hra.action_hra')

    def transition_create_hra_form(self):
        pool = Pool()
        vals = {}
        create_hra_form = []
        Hra = pool.get('hr.allowance.hra')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_hra_form.append(Hra.create([vals]))
        self.raises.hra_form = create_hra_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
