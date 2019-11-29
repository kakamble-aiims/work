from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow
from trytond.transaction import Transaction
from datetime import datetime
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button
from trytond.pyson import Eval, PYSONEncoder

_all_ = [
    'Conveyance_Allowance', 'ConveyanceEmployeeList', 'ConveyanceEmployee',
    'ConveyanceAllowanceWiz', 'ConveyanceList'
]


class Conveyance_Allowance(Workflow, ModelSQL, ModelView):
    """Employee Conveyance Allowance"""

    __name__ = 'employee_conveyance.allowance'

    salary_code = fields.Char(
        'Salary Code', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    employee = fields.Many2One(
        'company.employee', 'Employee Name',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    transport_amount = fields.Float(
        'Transport Amount',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
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
            ('confirm', 'Confirm'),
            ('account_officer', 'Account Officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
        ], 'Status', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "confirm": {
                'invisible': ~Eval('state').in_(
                    ['draft'
                     ]),
            },
            "submit": {
                'invisible': ~Eval('state').in_(
                    ['confirm'
                     ]),
            },
            "cancel": {
                'invisible': ~Eval('state').in_(
                    ['draft', 'account_officer'
                     ]),
            },
            "approve": {
                'invisible': ~Eval('state').in_(
                    ['account_officer'
                     ]),
            },
        })
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('draft', 'cancel'),
            ('confirm', 'account_officer'),
            ('account_officer', 'approve'),
            ('account_officer', 'cancel'),
        ))

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_from_date():
        return datetime.date.today()

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('account_officer')
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


class ConveyanceEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('conveyance.list', 'Employee List')


class ConveyanceEmployeeList(ModelView):
    'Conveyance Employee List'

    __name__ = 'conveyance.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many(
        'conveyance.list', 'conveyance_employee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class ConveyanceList(ModelSQL, ModelView):
    'Conveyance List'

    __name__ = 'conveyance.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    conveyance_employee_list = fields.Many2One(
        'conveyance.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class ConveyanceAllowanceWiz(Wizard):
    'Conveyance Allowance Wizard'

    __name__ = 'conveyance.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'conveyance.employee.list',
        'hr_conveyance.form_wiz_conveyance_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_conveyance_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_conveyance_form = StateTransition()
    open_ = StateAction('hr_conveyance.action_conveyance')

    def transition_create_conveyance_form(self):
        pool = Pool()
        vals = {}
        create_conveyance_form = []
        conveyance = pool.get('employee_conveyance.allowance')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_conveyance_form.append(conveyance.create([vals]))
        self.raises.conveyance_form = create_conveyance_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
