from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow
import datetime
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool, PoolMeta
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button
from trytond.transaction import Transaction

__all__ = [
    'HighDegreeAllowance', 'HdaEmployeeList', 'HdaEmployee',
    'HighDegreeAllowanceWiz', 'HdaList'
]


class HighDegreeAllowance(Workflow, ModelSQL, ModelView):
    'Higher Degree Qualification Allowance'

    __name__ = 'hr.allowance.hda'

    salary_code = fields.Char('Salary Code', required=True)
    employee = fields.Many2One('company.employee', 'Employee Name', required=True)
    designation = fields.Many2One('employee.designation', 'Designation', required=True)
    department = fields.Many2One('company.department', 'Department', required=True)
    hda_amount = fields.Float('Final HDA Amount', required=True,
        states={
        'readonly': ~Eval('state').in_(['draft']),
    }, depends=['state'])
    from_date = fields.Date('From Date', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    to_date = fields.Date('To Date', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
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
                    ['draft'
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


class HdaEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('hda.list', 'Employee List')


class HdaEmployeeList(ModelView):
    'HDA Employee List'

    __name__ = 'hda.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many('hda.list', 'hdaemployee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class HdaList(ModelSQL, ModelView):
    'HDA List'

    __name__ = 'hda.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    hdaemployee_list = fields.Many2One('hda.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class HighDegreeAllowanceWiz(Wizard):
    'High Degree Allowance Wizard'

    __name__ = 'hda.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'hda.employee.list',
        'hr_hda.form_wiz_hda_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_hda_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_hda_form = StateTransition()
    open_ = StateAction('hr_hda.action_hda')

    def transition_create_hda_form(self):
        pool = Pool()
        vals = {}
        create_hda_form = []
        hda = pool.get('hr.allowance.hda')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_hda_form.append(hda.create([vals]))
        self.raises.hda_form = create_hda_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
