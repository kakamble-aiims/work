from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction
from trytond.pyson import PYSONEncoder
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button


__all__ = [
    'NewspaperAllowance', 'TelephoneAllowance',
    'NewspaperEmployeeList', 'NewspaperEmployee',
    'NewspaperAllowanceWiz', 'NewspaperList',
    'TelephoneEmployeeList', 'TelephoneEmployee',
    'TelephoneAllowanceWiz', 'TelephoneList'
]


class NewspaperAllowance(ModelSQL, ModelView):
    'Employee Newspaper Bill Allowance'

    __name__ = 'newspaper.bill'

    salary_code = fields.Char('Salary Code', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    designation = fields.Many2One('employee.designation', 'Designation', required=True)
    department = fields.Many2One('company.department', 'Department', required=True)
    bill_amount = fields.Float('Bill Claim Amount' , required=True)
    bill_attachment = fields.Char('Bill Attachment')

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


class NewspaperEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('newspaper.list', 'Employee List')


class NewspaperEmployeeList(ModelView):
    'Newspaper Employee List'

    __name__ = 'newspaper.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many(
        'newspaper.list', 'newspaper_employee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class NewspaperList(ModelSQL, ModelView):
    'Newspaper Allowance List'

    __name__ = 'newspaper.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    newspaper_employee_list = fields.Many2One(
        'newspaper.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class NewspaperAllowanceWiz(Wizard):
    'Newspaper Allowance Wizard'

    __name__ = 'newspaper.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'newspaper.employee.list',
        'hr_bills.form_wiz_newspaper_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_newspaper_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_newspaper_form = StateTransition()
    open_ = StateAction('hr_bills.action_bills')

    def transition_create_newspaper_form(self):
        pool = Pool()
        vals = {}
        create_newspaper_form = []
        Newspaper = pool.get('newspaper.bill')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_newspaper_form.append(Newspaper.create([vals]))
        self.raises.newspaper_form = create_newspaper_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}


class TelephoneAllowance(ModelSQL, ModelView):
    'Employee Telephone Bill Allowance'

    __name__ = 'telephone.bill'

    salary_code = fields.Char('Salary Code', required=True)
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    designation = fields.Many2One('employee.designation', 'Designation', required=True)
    department = fields.Many2One('company.department', 'Department', required=True)
    bill_claim_amount = fields.Float('Bill Claim Amount', required=True)
    bill_attachment = fields.Char('Bill Attachment')

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


class TelephoneEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    employee_list = fields.Many2One('telephone.list', 'Employee List')


class TelephoneEmployeeList(ModelView):
    'Telephone Employee List'

    __name__ = 'telephone.employee.list'

    name = fields.Char('Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    employee = fields.One2Many(
        'telephone.list', 'telephone_employee_list', 'Employee')

    @staticmethod
    def default_start_date():
        return datetime.date.today()


class TelephoneList(ModelSQL, ModelView):
    'Telephone Allowance List'

    __name__ = 'telephone.list'

    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    amount = fields.Float('Amount')
    salary_code = fields.Char('Salary Code')
    telephone_employee_list = fields.Many2One(
        'telephone.employee.list', 'Employee List')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code if self.employee.salary_code else None
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None


class TelephoneAllowanceWiz(Wizard):
    'Telephone Allowance Wizard'

    __name__ = 'telephone.allowance.wiz'

    start_state = 'raises'
    raises = StateView(
        'telephone.employee.list',
        'hr_bills.form_wiz_telephone_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'submit',
                'create_telephone_form',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    create_telephone_form = StateTransition()
    open_ = StateAction('hr_bills.action_telephone')

    def transition_create_telephone_form(self):
        pool = Pool()
        vals = {}
        create_telephone_form = []
        telephone = pool.get('telephone.bill')
        for employee in self.raises.employee:
            vals = {
                'salary_code': employee.salary_code,
                'employee': employee.employee,
                'designation': employee.designation,
                'department': employee.department,
            }
            create_telephone_form.append(telephone.create([vals]))
        self.raises.telephone_form = create_telephone_form
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([])
        return action, {}
