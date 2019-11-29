import datetime
from trytond.model import Workflow
from trytond.model import (
    ModelView, ModelSQL, fields)
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction



__all__ = ['GPFAdvance', 'GPFreason', 'GPFCancelreason', 'GPFAdvanceLine']


class GPFAdvance(Workflow, ModelSQL, ModelView):
    'GPF Advance'
    __name__ = 'gpf.advance'

    salary_code = fields.Char("Salary Code",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    employee = fields.Many2One("company.employee", "Name of Subscriber",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    dob = fields.Date("Date of Birth",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    doj = fields.Date("Date of Joining",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    father_husband_name = fields.Char("Father's/Husband's Name",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    designation = fields.Many2One("employee.designation", "Designation",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    gpf_number = fields.Char("G.P.F.Number",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    account_no = fields.Char("S.B.I Ansari Nagar \n Saving A/c No",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    basic_pay = fields.Float("Basic Pay",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    amount_required = fields.Float("Amount Required",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    refund = fields.Selection([
        ('', 'None'),
        ('refundable', 'Refundable'),
        ('non_refund', 'Non Refundable'),
    ], string='Refund',
        states={
                'readonly': ~Eval('state').in_(['draft']),
            }, depends=['state'], required=True)
    gpf_reason = fields.Many2One("gpf.reason",
        "Reason for which advance/withdrawal is Required",
        domain=[('refund', '=', Eval('refund'))],
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],required=True)
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
    installment_no = fields.Integer("Number of installment")
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
        ], 'Status', readonly=True
    )
    gpf_balance = fields.Float("G.P.F.Amount",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    amount = fields.Float("installment Amount",
        states={
            'invisible': Eval('refund').in_(['non_refund']),
        }, depends=['state'])
    cancel_reason = fields.Many2One('gpf.cancel.reason', 'Cancel Reason',
        states={
            'invisible': ~Eval(
                'state').in_(['forwarded_to_ao', 'cancel']),
            'readonly': ~Eval('state').in_(['forwarded_to_ao']),
             }, depends=['state'],)
    gpf_line = fields.One2Many(
        'gpf.advance.line', 'gpf_advance', 'Installment Lines')
    payout = fields.Float('Payout',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
            #'required': Eval('refund').in_(['refundable']),
        }, depends=['state'])
    pending = fields.Float('Pending',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
            #'required': Eval('refund').in_(['refundable']),
        }, depends=['state'])
    reschedule = fields.Float('Reschedule',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
            #'required': Eval('refund').in_(['refundable']),
        }, depends=['state'])

    @classmethod
    def validate(cls, records):
        super(GPFAdvance, cls).validate(records)
        years = 0
        for record in records:
            if record.doj:
                x = datetime.datetime.now().date() - record.doj
                years = int(x.days/365)
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
        if self.installment_no and self.installment_no > 60:
            self.raise_user_error('Installment Number is not max 60')

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

    @classmethod
    @ModelView.button
    @Workflow.transition('forwarded_to_jo')
    def submitted_to_ao(cls, records):
        cls.gpf_installment(records)
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
        self.salary_code = self.employee.salary_code
        self.doj = self.employee.date_of_joining
        self.designation = self.employee.designation
        self.dob = self.employee.party.dob
        self.gpf_number = self.employee.gpf_number
        self.father_husband_name = self.employee.father_name
        self.gpf_balance = self.employee.gpf_balance
        pool = Pool()
        hrcontract = pool.get('hr.contract')
        contracts = hrcontract.search([
            ('employee', '=', self.employee),
            ('active', '<=', True)
            ])
        for contract in contracts:
            self.basic_pay = contract.basic

    @fields.depends('refund')
    def on_change_refund(self, name=None):
        self.gpf_reason = None

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
            if  'installment_no' in values.keys():
                cls.change_gpf_installment(mechanisms,values)
        super(GPFAdvance, cls).write(*args)

    @classmethod
    def change_gpf_installment(cls, records, values):
        cursor = Transaction().connection.cursor()
        GPFLine = Pool().get('gpf.advance.line')
        for gpf in records:
            cursor.execute('SELECT sum(amount) FROM gpf_advance_line WHERE gpf_advance=%s \
                AND status = %s', (gpf.id,'done'))
            total_amount = cursor.fetchone()
            if total_amount[0]:
                reschedule = gpf.amount_required - total_amount[0]
                cls.write(records, {'payout': total_amount[0],
                                    'reschedule': reschedule})
                amount = (reschedule/values['installment_no'])
            else:
                amount = (gpf.amount_required/values['installment_no'])
            cursor.execute('delete FROM gpf_advance_line WHERE gpf_advance=%s \
            AND status != %s', (gpf.id,'done'))
            count = 0
            for line in range(1,int(values['installment_no'])+1):
                mydate = datetime.datetime.now().month
                month = mydate - 1
                if month+line > 12:
                    count +=1
                    if count > 12:
                        count = 1
                    months = datetime.date(1900, count, 1).strftime('%B')
                else:
                    months = datetime.date(1900, month+line, 1).strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'gpf_advance': gpf.id
                }
                line = GPFLine.create([vals])

    @classmethod
    def gpf_installment(cls, records):
        cursor = Transaction().connection.cursor()
        GPFLine = Pool().get('gpf.advance.line')
        for gpf in records:
            amount = (gpf.amount_required/gpf.installment_no)
            for line in range(1,int(gpf.installment_no)+1):
                mydate = datetime.datetime.now().month
                month = mydate - 1
                if month+line > 12:
                    count +=1
                    if count > 12:
                        count = 1
                    months = datetime.date(1900, count, 1).strftime('%B')
                else:
                    months = datetime.date(1900, month+line, 1).strftime('%B')
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
                    'gpf_balance': (gpf_bal.gpf_balance - gpf_bal.amount_required),
                    })

    
class GPFreason(ModelSQL, ModelView):
    'GPF Reason'

    __name__ = 'gpf.reason'
    _rec_name = 'name'

    name = fields.Char("Reason")
    refund = fields.Selection([
        ('', 'None'),
        ('refundable', 'Refundable'),
        ('non_refund', 'Non Refundable'),
    ], string='Refund',)


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
        ('done', 'Done'),
    ], string='Status',)
    gpf_advance = fields.Many2One("gpf.advance", "GPF Advance")

    @staticmethod
    def default_status():
        return 'pending'

# class ModifyInstallment(Wizard):
#     "Modify Installment"
#     __name__ = 'gpf.modify_installment'

