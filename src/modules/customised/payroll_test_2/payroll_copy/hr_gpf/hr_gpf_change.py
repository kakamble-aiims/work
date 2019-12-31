import requests
import random
from datetime import datetime
from trytond.model import Workflow
from trytond.model import (
    ModelView, ModelSQL, fields)
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from trytond.transaction import Transaction
from dateutil.relativedelta import relativedelta


__all__ = ['GPFSubscription', 'HrContract', 'HrEmployee']


class GPFSubscription(Workflow, ModelSQL, ModelView):
    'GPF Subscription'
    __name__ = 'gpf.subscription'

    salary_code = fields.Char('Salary Code', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    employee = fields.Many2One('company.employee', 'Employee', required=True,
        domain=[('gpf_number', '!=', None)],
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    doj = fields.Date('Date of Joining',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    designation = fields.Many2One('employee.designation', 
                'Designation', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    department = fields.Many2One('company.department', 
                'Department', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    gpf_number = fields.Char('G.P.F.Number', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
        )
    basic_pay = fields.Float('Basic Pay',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True
        )
    change_sub = fields.Selection([
        ('increase', 'Increase'),
        ('decrease', 'Decrease'),
    ], string='Change Subscription', required=True, sort=False,
        states={
            'readonly': ~Eval('state').in_(['draft', 'waiting_for_otp']),
        }, depends=['state']
        )
    pre_amount = fields.Float('Current Subscription',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True
        )
    curr_amount = fields.Float('Request Subscription', required=True,
        states={
            'readonly': ~Eval('state').in_(['draft', 'waiting_for_otp']),
        }, depends=['state']
        )
    otp = fields.Char('OTP', size=6,
                      states={
                              'invisible': ~Eval(
                                'state').in_(['waiting_for_otp']),
                             }, depends=['state'],)
    otp_generate = fields.Char('OTP Generated')
    otp_generate_time = fields.DateTime('OTP Generated Time')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_otp', 'Waiting For OTP'),
        ('submitted_to_ao', 'Forwarded to AO'),
        ('approved', 'Approved'),
        ('cancel_gpf', 'Cancel'),
    ], 'Status', readonly=True, sort=False)
    contract = fields.Many2One('hr.contract', 'Salary Details',
        states={
            'invisible': ~Eval(
                'state').in_([])}
        )
    reason = fields.Char('Reason',
        states={
            'invisible': ~Eval(
                'state').in_(['submitted_to_ao', 'cancel_gpf']),
            'readonly': ~Eval('state').in_(['submitted_to_ao']),
             }, depends=['state'],)
    approve_date = fields.Date('Date of Approve',
        states={
            'invisible': ~Eval(
                'state').in_(['approved']),
            'readonly': Eval('state').in_(['approved']),
             }, depends=['state'],)
    gpf_balance = fields.Float('G.P.F.Amount')

    @staticmethod
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    @fields.depends('employee')
    def on_change_employee(self, name=None):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.doj = self.employee.date_of_joining
            self.designation = self.employee.designation
            self.department = self.employee.department
            self.gpf_number = self.employee.gpf_number
            pool = Pool()
            hrcontract = pool.get('hr.contract')
            contracts = hrcontract.search([
                ('employee', '=', self.employee)
                ])
            for contract in contracts:
                self.contract = contract.id
                self.basic_pay = contract.basic
                self.pre_amount = contract.gpf_amount

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_change_sub():
        return 'increase'

    @classmethod
    def validate(cls, records):
        super(GPFSubscription, cls).validate(records)
        for record in records:
            approvedate = datetime.now() - relativedelta(months=3)
            year = datetime.now().year
            start_date = datetime(year, 4, 1).date()
            end_date = datetime((year+1), 3, 31).date()
            gpf_sub = cls.search([
                    ('id', '!=', record.id),
                    ('employee', '=', record.employee),
                    ('state', '=', 'approved')
                    ])
            if gpf_sub:
                gpf = cls.search([
                        ('id', '!=', record.id),
                        ('employee', '=', record.employee),
                        ('state', '=', 'approved'),
                        ('approve_date', '>=', approvedate.date()),
                        ])
                gpf_increase = cls.search([
                        ('id', '!=', record.id),
                        ('employee', '=', record.employee),
                        ('change_sub', '=', 'increase'),
                        ('state', '=', 'approved'),
                        ('approve_date', '>=', start_date),
                        ('approve_date', '<=', end_date)
                        ])
                gpf_decrease = cls.search([
                        ('id', '!=', record.id),
                        ('employee', '=', record.employee),
                        ('change_sub', '=', 'decrease'),
                        ('state', '=', 'approved'),
                        ('approve_date', '>=', start_date),
                        ('approve_date', '<=', end_date)
                        ])
                if gpf:
                    cls.raise_user_error('Need for 3 Month GAP')
                if record.change_sub == 'increase' and len(gpf_increase) >= 2:
                    cls.raise_user_error('Already 2 times increase in the year')
                elif record.change_sub == 'decrease' and len(gpf_decrease) >= 1:
                    cls.raise_user_error('Already 1 times decrease in the year')
            record.valid_curr_amount()

    def valid_curr_amount(self):
        if self.basic_pay:
            basic = (6 * self.basic_pay)/100
        if self.basic_pay < self.curr_amount:
            self.raise_user_error('Current Amount maximum of basic amount')
        elif basic > self.curr_amount:
            self.raise_user_error('Current Amount minmum of basic amount 6%')
        elif (
                self.change_sub == 'increase'
                and
                self.pre_amount >= self.curr_amount):
            self.raise_user_error('Current Amount minmum of Previous amount')
        elif (
                self.change_sub == 'decrease'
                and
                self.pre_amount <= self.curr_amount):
            self.raise_user_error('Current Amount maximum of Previous amount')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'otp_error': "OTP is not fill",
        })
        cls._transitions |= set((
            ('draft', 'waiting_for_otp'),
            ('waiting_for_otp', 'submitted_to_ao'),
            ('submitted_to_ao', 'approved'),
            ('submitted_to_ao', 'cancel_gpf'),
            ))
        cls._buttons.update({
                'waiting_for_otp': {
                    'invisible': ~Eval('state').in_(
                        ['draft']),
                    'depends': ['state'],
                    },
                'submitted_to_ao': {
                    'invisible': ~Eval('state').in_(
                        ['waiting_for_otp']),
                    'depends': ['state'],
                    },
                'approved': {
                    'invisible': ~Eval('state').in_(
                        ['submitted_to_ao']),
                    'depends': ['state'],
                    },
                'cancel_gpf': {
                    'invisible': ~Eval('state').in_(
                        ['submitted_to_ao']),
                    'depends': ['state'],
                    },
                })

    @classmethod
    def create(cls, values):
        '''Overwrite the method to manage the parts.'''
        for vals in values:
            gpf_increase = cls.search([
                    ('employee', '=', vals['employee']),
                    ('change_sub', '=', 'increase'),
                    ('state', 'not in', ('approved', 'cancel_gpf'))
                    ])
            gpf_decrease = cls.search([
                    ('employee', '=', vals['employee']),
                    ('change_sub', '=', 'decrease'),
                    ('state', 'not in', ('approved', 'cancel_gpf'))
                    ])
            if gpf_increase:
                cls.raise_user_error('Please Approve Previous GPF')
            if gpf_decrease:
                cls.raise_user_error('Please Approve Previous GPF')
        return super().create(values)

    def notify_otp_to_user(self):
        message = """Dear {name}, OTP to digitally submitted_to_ao
            the GPF form is {otp}""".format(name=self.employee.party.name,
                                            otp=self.otp_generate)
        # TODO: Get the value of logged in user's employee.
        contact = self.employee.party.contact_mechanism_get('mobile')
        if not contact:
            self.raise_user_error("missing_contact")
        number = contact.value
        number = 8171733480
        params = {
            'msg': message + " (%s)" % contact.value,
            'mobile': number,
        }
        url = "http://192.168.185.17/trytonsms/sendsms.aspx"
        requests.get(url, params)
        return True

    def generate_otp(self):
        # Generate OTP for the user
        self.otp_generate = ''.join(
            ["%s" % random.randint(0, 9) for num in range(0, 6)])
        self.otp_generate_time = datetime.now()
        self.save()
        self.notify_otp_to_user()

    def validate_otp(self):
        # Validate OTP
        if self.otp != self.otp_generate:
            self.raise_user_error('invalid_otp')
        return True

    @classmethod
    @ModelView.button
    @Workflow.transition('waiting_for_otp')
    def waiting_for_otp(cls, records):
        for record in records:
            record.state = 'draft'
            record.save()
            record.generate_otp()

    @classmethod
    @ModelView.button
    @Workflow.transition('submitted_to_ao')
    def submitted_to_ao(cls, records):
        for record in records:
            record.validate_otp()
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approved')
    def approved(cls, records):
        cls.set_gpf_amount(records)
        cls.generate_gpf_lines(records)
       

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel_gpf')
    def cancel_gpf(cls, records):
        for record in records:
            if not record.reason:
                cls.raise_user_error('Please fill the reason')
        pass

    @classmethod
    def set_gpf_amount(cls, records):
        '''
        Fill the number field with the sale sequence
        '''
        pool = Pool()
        contract = pool.get('hr.contract')
        for gpf in records:
            if not gpf.otp:
                cls.raise_user_error('OTP is not fill')
            if gpf.contract:
                gpf.approve_date = datetime.now().date()
                gpf.save()
                contract.write([gpf.contract], {
                    'gpf_amount': gpf.curr_amount,
                    })

    
class HrContract(metaclass=PoolMeta):
    "HR Contract"

    __name__ = 'hr.contract'

    gpf_amount = fields.Float('GPF Amount')

    @fields.depends('basic')
    def on_change_basic(self, name=None):
        if self.employee.gpf_nps == 'gpf':
            if self.basic and self.gpf_amount == None:
                self.gpf_amount = (6 * self.basic)/100


class HrEmployee(metaclass=PoolMeta):
    'HR Employee'

    __name__ = 'company.employee'

    gpf_number = fields.Char('G.P.F.Number')
    gpf_balance = fields.Float('G.P.F.Balance')
    gpf_nps = fields.Selection([
        ('gpf', 'GPF'),
        ('nps', 'NPS'),
    ], 'Status', sort=False)
    gpf_book = fields.One2Many(
        'hr.gpf.lines',
        'gpf_lines', string='Employee GPF Book')

    @fields.depends('date_of_joining')
    def on_change_date_of_joining(self, name=None):
        if self.date_of_joining:
            if self.date_of_joining.year <= 2004:
                self.gpf_nps = 'gpf'
            elif self.date_of_joining.year >= 2004:
                self.gpf_nps = 'nps'

    @classmethod
    def view_attributes(cls):
        super(HrEmployee, cls).view_attributes()
        gpf = ~Eval('gpf_nps').in_(['gpf'])
        attribute = [
            ("//page[@id='employee_gpf_details']", "states", {"invisible": gpf}),
        ]
        return attribute

    
    @classmethod
    def set_gpf_interest(cls):
        pool = Pool()
        gpf_lines_data = pool.get('hr.gpf.lines')
        records = cls.search([()])
        # year = datetime.now().year
        # start_date = datetime(year, 4, 1).date()
        # end_date = datetime((year+1), 3, 31).date()
        for record in records:
            if record.gpf_balance:
                vals = {
                    'amount': (float(record.gpf_balance) * 7.9)/(12 * 100),
                    'date' : datetime.now().date(),
                    'description' : 'ABCCCCCCCC',
                    'gpf_lines' : record.id,
                    'gpf_type' : 'interest'
                }
                line = gpf_lines_data.create([vals])
        