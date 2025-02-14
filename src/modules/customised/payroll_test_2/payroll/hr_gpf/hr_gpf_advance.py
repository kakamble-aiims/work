from datetime import date, datetime
from dateutil import relativedelta
from trytond.model import ModelSQL, ModelView, Workflow, fields
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction


__all__ = ['GPFAdvance', 'GPFreason', 'GPFCancelreason', 'GPFAdvanceLine']


class GPFAdvance(Workflow, ModelSQL, ModelView):
    'GPF Advance'
    __name__ = 'gpf.advance'

    salary_code = fields.Char(
        "Salary Code", required=True, 
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    employee = fields.Many2One(
        "company.employee", "Name of Subscriber", required=True,
        domain=[('gpf_number', '!=', None)],
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    dob = fields.Date("Date of Birth",states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    doj = fields.Date(
        "Date of Joining", states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    father_husband_name = fields.Char(
        "Father's/Husband's Name",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    designation = fields.Many2One(
        "employee.designation", "Designation", required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    department = fields.Many2One(
        "company.department", "Department", required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    gpf_number = fields.Char(
        "G.P.F.Number", required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    basic_pay = fields.Float(
        "Basic Pay",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    amount_required = fields.Float(
        "Amount Required",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    refund = fields.Selection([
        ('refundable', 'Refundable'),
        ('non_refund', 'Non Refundable'),
    ], string='Refund', sort=False,
        states={
        'readonly': ~Eval('state').in_(['draft']),
    }, depends=['state'], required=True)
    gpf_reason = fields.Many2One(
        "gpf.reason",
        "Reason for which advance/withdrawal is Required",
        domain=[('refund', '=', Eval('refund'))],
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state', 'refund'], required=True)
    location = fields.Char("Location of the Plot",
                           states={
                               'readonly': ~Eval('state').in_(['draft']),
                           }, depends=['state'])
    hold = fields.Char("Whether plot is \n free hold",
                       states={
                           'readonly': ~Eval('state').in_(['draft']),
                       }, depends=['state'])
    cost = fields.Float("Cost of Construction",
                        states={
                            'readonly': ~Eval('state').in_(['draft']),
                        }, depends=['state'])
    installment_no = fields.Integer("Number of installment",
        states={
           'invisible': ~Eval('refund').in_(['refundable']),
           'required': Eval('refund').in_(['refundable']),
       }, depends=['refund'])
    # states={
    #     'readonly': ~Eval('state').in_(['draft']),
    #     'invisible': ~Eval('refund').in_(['refundable']),
    #     'required': Eval('refund').in_(['refundable']),
    # }, depends=['state'])
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('forwarded_to_jo', 'Forwarded to JO'),
            ('forwarded_to_ao', 'Forwarded to AO'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
        ], 'Status', readonly=True, sort=False
    )
    gpf_balance = fields.Float("G.P.F.Amount",
       states={
           'readonly': ~Eval('state').in_(['draft']),
       }, depends=['state'])
    amount = fields.Float("installment Amount",
        states={
            'invisible': Eval('refund').in_(['non_refund']),
        }, depends=['refund'])
    cancel_reason = fields.Many2One(
        'gpf.cancel.reason', 'Cancel Reason',
        states={
            'invisible': ~Eval(
                'state').in_(['forwarded_to_ao', 'cancel']),
            'readonly': ~Eval('state').in_(['forwarded_to_ao']),
        }, depends=['state'],)
    gpf_line = fields.One2Many(
        'gpf.advance.line', 'gpf_advance', 'Installment Lines')
    payout = fields.Float('Payout',
        states={
            'invisible': ~Eval('refund').in_(['refundable']) and Eval('state').in_(['draft'])
        }, depends=['state', 'refund'], readonly=True)
    pending = fields.Float(
        'Pending',
        states={
            'invisible': ~Eval('refund').in_(['refundable']) and Eval('state').in_(['draft']),
        }, depends=['state', 'refund'], readonly=True)
    reschedule = fields.Float(
        'Reschedule',
        states={
            'invisible': ~Eval('refund').in_(['refundable']) and Eval('state').in_(['draft'])
        }, depends=['state', 'refund'], readonly=True)
    check = fields.Boolean('Check',
        states={
            'invisible': Eval('state').in_(['draft','forwarded_to_ao','forwarded_to_jo', 'approve','cancel']),
        }, depends=['state'])
    gpf_file_no = fields.Char(
        "GPF File No.",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    age = fields.Integer("Age")
        

    @classmethod
    def validate(cls, records):
        super(GPFAdvance, cls).validate(records)
        years = 0
        for record in records:
            if record.doj:
                x = datetime.now().date() - record.doj
                years = int(x.days / 365)
            if years < 10 and record.refund == 'non_refund':
                cls.raise_user_error('Non Refund only apply \
                                      after 10 year of Joining')
            record.valid_curr_amount()
            record.valid_installment_num()

    def valid_curr_amount(self):
        if self.gpf_balance:
            balance = (0.75 * self.gpf_balance)
        if balance < self.amount_required:
            self.raise_user_error('Current Amount maximum of \
                                   75% of GPF Balance')

    def valid_installment_num(self):
        now = datetime.now().date()
        diff = relativedelta.relativedelta(now, self.dob)
        years = diff.years
        months = diff.months
        if self.installment_no and self.installment_no > 60:
            self.raise_user_error('Installment Number is not max 60')
        if self.reschedule and self.reschedule > 60:
            self.raise_user_error('Installment Number is not max 60')
        if self.age >= 55:
            left_month = (60 - self.age)
            total_month = left_month * 12
            left_time = (total_month + months) - 3
            if self.installment_no > left_time:
                self.raise_user_error('Employee must be pay this installment {} months '.format(left_time))
        if (years > 59) or (years == 59 and months >= 9):
            self.raise_user_error('you are not eligible to fill this')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'forwarded_to_jo'),
            ('forwarded_to_jo', 'forwarded_to_ao'),
            ('forwarded_to_ao', 'approve'),
            ('forwarded_to_ao', 'cancel'),
        ))
        cls._buttons.update({
            'calculate': {
                'invisible': ~Eval('refund').in_(
                    ['refundable']),
                'depends': ['refund'],
            },
            'submitted_to_ao': {
                'invisible': ~Eval('state').in_(
                    ['draft']),
                'depends': ['state'],
            },
            'forward_to_jo': {
                'invisible': ~Eval('state').in_(
                    ['forwarded_to_jo']),
                'depends': ['state'],
            },
            'forward_to_ao': {
                'invisible': ~Eval('state').in_(
                    ['forwarded_to_ao']),
                'depends': ['state'],
            },
            'cancel': {
                'invisible': ~Eval('state').in_(
                    ['forwarded_to_ao']),
                'depends': ['state'],
            },
        })

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_refund():
        return 'refundable'

    @classmethod
    def view_attributes(cls):
        super().view_attributes()
        installment = ~Eval('refund').in_(['refundable'])
        attribute = [
            ("//page[@id='gpf_advance_line']", "states", {"invisible": installment}),
        ]
        return attribute

    @classmethod
    def calculate(cls, records):
        for record in records:
            print(record.check, "record.check")
            if record.check == False:
                cls.gpf_installment(records)
                record.check = True
                record.save()
    
    @classmethod
    @ModelView.button
    @Workflow.transition('forwarded_to_jo')
    def submitted_to_ao(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('forwarded_to_ao')
    def forward_to_jo(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approve')
    def forward_to_ao(cls, records):
        cls.change_gpf_balance(records)
        cls.generate_gpf_lines(records)
        pass
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        for record in records:
            if not record.cancel_reason:
                cls.raise_user_error('Please fill the Cancel reason')
        pass

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
            self.designation = self.employee.designation
            self.department = self.employee.department
            self.doj = self.employee.date_of_joining
            self.designation = self.employee.designation
            self.dob = self.employee.party.dob
            self.gpf_number = self.employee.gpf_number
            self.father_husband_name = self.employee.father_name
            self.gpf_balance = self.employee.gpf_balance
            pool = Pool()
            hrcontract = pool.get('hr.contract')
            contracts = hrcontract.search([
                ('employee', '=', self.employee)
            ])
            for contract in contracts:
                self.basic_pay = contract.basic
            if self.employee.party.dob:
                now = datetime.now()
                diff = relativedelta.relativedelta(now, self.employee.party.dob)
                years = diff.years
                self.age = years

    @fields.depends('refund')
    def on_change_refund(self, name=None):
        self.gpf_reason = None
    
    @fields.depends('dob')
    def on_change_dob(self, name=None):
        if self.dob:
            now = datetime.now().date()
            diff = relativedelta.relativedelta(now, self.dob)
            years = diff.years
            self.age = years

    @classmethod
    def create(cls, values):
        '''Overwrite the method to manage the parts.'''
        for vals in values:
            gpf_balance = (0.75 * vals['gpf_balance'])
            if vals['amount_required'] > gpf_balance:
                cls.raise_user_error('Please change Required Amount.\
                    Because you can apply only max 75% 0f GPF Balance')
        return super(GPFAdvance, cls).create(values)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for mechanisms, values in zip(actions, actions):
            if 'installment_no' in values.keys():
                cls.change_gpf_installment(mechanisms, values)
        super(GPFAdvance, cls).write(*args)

    @classmethod
    def change_gpf_installment(cls, records, values):
        cursor = Transaction().connection.cursor()
        GPFLine = Pool().get('gpf.advance.line')
        for gpf in records:
            cursor.execute('SELECT sum(amount) FROM gpf_advance_line \
                WHERE gpf_advance=%s \
                AND status = %s', (gpf.id, 'done'))
            total_amount = cursor.fetchone()
            if total_amount[0]:
                pending = gpf.amount_required - total_amount[0]
                cls.write(records, {'payout': total_amount[0],
                                    'pending': pending,
                                    'reschedule' : 1})
                amount = (pending / values['installment_no'])
            else:
                amount = (gpf.amount_required / values['installment_no'])
            cursor.execute('delete FROM gpf_advance_line WHERE gpf_advance=%s \
            AND status != %s', (gpf.id, 'done'))
            count = 0
            for line in range(1, int(values['installment_no']) + 1):
                mydate = datetime.now().month
                if total_amount[0]:
                    month = mydate
                else: 
                    month = mydate - 1
                if month + line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime.date(1900, count, 1).strftime('%B')
                else:
                    months = datetime.date(
                        1900, month + line, 1).strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'gpf_advance': gpf.id
                }
                line = GPFLine.create([vals])

    @classmethod
    def gpf_installment(cls, records):
        GPFLine = Pool().get('gpf.advance.line')
        for gpf in records:
            amount = (gpf.amount_required / gpf.installment_no)
            count = 0
            for line in range(1, int(gpf.installment_no)+1):
                mydate = datetime.now().month
                month = mydate - 1
                if month+line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime.now().date().replace(1900, count, 1).strftime('%B')
                else:
                    months = datetime.now().date().replace(1900, month+line, 1).strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'gpf_advance': gpf.id
                }
                line = GPFLine.create([vals])

    @classmethod
    def change_gpf_balance(cls, records):
        pool = Pool()
        employee = pool.get('company.employee')
        for gpf_bal in records:
            if gpf_bal.employee:
                employee.write([gpf_bal.employee], {
                    'gpf_balance': (gpf_bal.gpf_balance
                                    - gpf_bal.amount_required),
                })

    @classmethod
    def generate_gpf_lines(cls, records):
        pool = Pool()
        gpf_lines_data = pool.get('hr.gpf.lines')
        for record in records:
            if record.refund == 'refundable':
                refund = 'advance'
            else:
                refund = 'withdraw'
            vals = {
                'amount': record.amount_required,
                'date' : datetime.now().date(),
                'description' : 'ABCCCCCCCC',
                'gpf_type' : refund,
                'gpf_lines' : record.employee
            }
        line = gpf_lines_data.create([vals])


class GPFreason(ModelSQL, ModelView):
    'GPF Reason'

    __name__ = 'gpf.reason'
    _rec_name = 'name'

    name = fields.Char("Reason")
    refund = fields.Selection([
        ('refundable', 'Refundable'),
        ('non_refund', 'Non Refundable'),
    ], string='Refund', sort=False)


class GPFCancelreason(ModelSQL, ModelView):
    'GPF Cancel Reason'

    __name__ = 'gpf.cancel.reason'
    _rec_name = 'name'

    name = fields.Char("Cancel Reason")


class GPFAdvanceLine(ModelSQL, ModelView):
    'GPF Advance Lines'

    __name__ = 'gpf.advance.line'
    _rec_name = 'month'

    month = fields.Char("Month")
    amount = fields.Float("Amount")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('inprogress', 'In-Progress'),
        ('done', 'Done'),
    ], string='Status', sort=False)
    gpf_advance = fields.Many2One("gpf.advance", "GPF Advance")

    @staticmethod
    def default_status():
        return 'pending'


