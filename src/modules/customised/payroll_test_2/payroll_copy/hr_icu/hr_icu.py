from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.pool import Pool, PoolMeta
import datetime
from trytond.pyson import Eval, PYSONEncoder
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button
from trytond.transaction import Transaction

__all__ = [
    'ICUAllowance', 'IcuEmployeeList', 'IcuEmployee',
    'ICUAllowanceWiz', 'IcuList'
]


class ICUAllowance(Workflow, ModelSQL, ModelView):
    """ICU Allowance for an Employee"""

    __name__ = 'hr.allowance.icu'

    _STATES = {
        'readonly': ~Eval('state').in_(['draft'])
    }
    _DEPENDS = ['state']
    salary_code = fields.Char(
        'Salary Code', required=True, states=_STATES, depends=_DEPENDS)
    employee = fields.Many2One(
        'company.employee', 'Employee Name', required=True,
        states=_STATES, depends=_DEPENDS
    )
    designation = fields.Many2One(
        'employee.designation', 'Designation', required=True,
        states=_STATES, depends=_DEPENDS
    )
    department = fields.Many2One(
        'company.department', 'Department', required=True,
        states=_STATES, depends=_DEPENDS
    )
    amount = fields.Integer('ICU Amount', states=_STATES, required=True, depends=_DEPENDS)
    from_date = fields.Date(
        'From Date',
        states=_STATES, depends=_DEPENDS
    )
    to_date = fields.Date(
        'To Date',
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
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_from_date():
        return datetime.date.today()

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


class IcuEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('icu.list', 'Employee List')


class IcuEmployeeList(ModelView):
    'ICU Employee List'

    __name__ = 'icu.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many('icu.list', 'icuemployee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class IcuList(ModelSQL, ModelView):
    'ICU List'

    __name__ = 'icu.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    icuemployee_list = fields.Many2One('icu.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class ICUAllowanceWiz(Wizard):
    'ICU Allowance Wizard'

    __name__ = 'icu.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'icu.employee.list',
        'hr_icu.form_wiz_icu_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_icu_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_icu_form = StateTransition()
    open_ = StateAction('hr_icu.action_icu')

    def transition_create_icu_form(self):
        pool = Pool()
        vals = {}
        create_icu_form = []
        icu = pool.get('hr.allowance.icu')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
                'amount': employee.amount

            }
            create_icu_form.append(icu.create([vals]))
        self.raises.icu_form = create_icu_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
