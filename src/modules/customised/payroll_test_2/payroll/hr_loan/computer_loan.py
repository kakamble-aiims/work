from datetime import datetime
from trytond.model import Workflow
from trytond.model import (
    ModelView, ModelSQL, fields)
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction
from dateutil import relativedelta

__all__ = ['ComputerLoan', 'LoanCancelreason', 'ComputerloanLine']


class ComputerLoan(Workflow, ModelSQL, ModelView):
    'Computer Loan'
    __name__ = 'computer.loan'

    salary_code = fields.Char('Salary Code',
                              states={
                                  'readonly': ~Eval('state').in_(['draft']),
                              }, depends=['state'], required=True)
    employee = fields.Many2One('company.employee', 'Name of Applicant',
                               states={
                                   'readonly': ~Eval('state').in_(['draft']),
                               }, depends=['state'], required=True)
    designation = fields.Many2One(
        "employee.designation",
        "Applicant's Designation",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    department = fields.Many2One('company.department', 'Department',
                                 states={
                                     'readonly': ~Eval('state').in_(['draft']),
                                 }, depends=['state'], required=True)
    pay_in_band = fields.Char('Pay in the Pay Band',
                              states={
                                  'readonly': ~Eval('state').in_(['draft']),
                              }, depends=['state'])
    price = fields.Float('Price of Personal Computer',
                         required=True,
                         states={
                             'readonly': ~Eval('state').in_(['draft']),
                         }, depends=['state'])
    amount_required = fields.Float(
        "Amount Required",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    date_of_retirement = fields.Date(
        'Date of Retirement',
        required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    dob = fields.Date("Date of Birth",
                      states={
                          'readonly': ~Eval('state').in_(['draft']),
                      }, depends=['state'], required=True)
    installment_no = fields.Integer("Number of instalment",
                                    required=True)
    purpose = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Purpose',
        states={
        'readonly': ~Eval('state').in_(['draft']),
    }, depends=['state'], required=True)
    drawal_date = fields.Date('Date of drawal of advance',
                              states={
                                  'invisible': ~Eval('purpose').in_(['yes']),
                                  'required': Eval('purpose').in_(['yes']),
                              }, depends=['purpose'])
    interest = fields.Float('Interest',
                            states={
                                'invisible': ~Eval('purpose').in_(['yes']),
                                'required': Eval('purpose').in_(['yes']),
                            }, depends=['purpose'])
    basic_pay = fields.Float("Basic Pay",
                             states={
                                 'readonly': ~Eval('state').in_(['draft']),
                             }, depends=['state'])
    cancel_reason = fields.Many2One(
        'loan.cancel.reason', 'Cancel Reason',
        states={
            'invisible': ~Eval(
                'state').in_(['forwarded_to_ao', 'cancel']),
            'readonly': ~Eval('state').in_(['forwarded_to_ao']),
        }, depends=['state'],)
    payout = fields.Float('Payout',
                          states={
                              'readonly': ~Eval('state').in_(['draft']),
                              'invisible': ~Eval('refund').in_(['refundable']),
                          }, depends=['state'])
    pending = fields.Float(
        'Pending',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
        }, depends=['state'])
    reschedule = fields.Float(
        'Reschedule',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
        }, depends=['state'])
    loan_line = fields.One2Many(
        'computer.loan.line', 'loan', 'Installment Lines',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    approve_date = fields.Date('Date of Approval',
                               states={
                                   'invisible': ~Eval('state').in_(['approve'])
                               }, depends=['state'], readonly=True)
    approve_by = fields.Many2One(
        'res.user', 'Approved By',
        states={
            'invisible': ~Eval('state').in_(['approve'])
        }, depends=['state'], readonly=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('forwarded_to_jo', 'Forwarded to JO'),
            ('forwarded_to_ao', 'Forwarded to AO'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
        ], 'Status', readonly=True
    )
    check = fields.Boolean('Check',
                           states={
                               'invisible': Eval('state').in_(['draft', 'forwarded_to_ao', 'forwarded_to_jo', 'approve', 'cancel']),
                           }, depends=['state'])

    @classmethod
    def validate(cls, records):
        """Method to validate records(rows) in a model(table)"""
        super().validate(records)
        for record in records:
            if record.installment_no < 1:
                cls.raise_user_error(
                    'Number of Installment can not less than 1. Please correct it.')
            if record.price > float(50000) and record.amount_required > float(50000):
                cls.raise_user_error(
                    'The Required Amount can not be greater than Rs. 50,000/-. Please correct it.')

            if record.installment_no > 150:
                cls.raise_user_error(
                    'As per GoI rules, there can not be more than 150 insallments. Please correct it.')
            computer_loan = cls.search([
                ('id', '!=', record.id),
                ('employee', '=', record.employee),
                ('state', '=', 'approve')])
            if computer_loan and len(computer_loan) >= 5:
                cls.raise_user_error(
                    'You are not allowed to take computer loan more than 5 times.')
            approvedate = datetime.now().date()
            approve = approvedate.replace(year=approvedate.year-3)
            if computer_loan and computer_loan[-1].approve_date > approve:
                cls.raise_user_error(
                    'You are not allowed to take computer loan with in 3 years from the previous computer loan.')

    @classmethod
    def __setup__(cls):
        """Setup workflow transitions and button properties
           when an instance of this class is initialized"""
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'forwarded_to_jo'),
            ('forwarded_to_jo', 'forwarded_to_ao'),
            ('forwarded_to_ao', 'approve'),
            ('forwarded_to_ao', 'cancel'),
        ))
        cls._buttons.update({
            'calculate_instalment': {},
            'submitted_to_jo': {
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
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    @staticmethod
    def default_salary_code():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.salary_code if employee else None

    @staticmethod
    def default_designation():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.designation.id if employee else None

    @staticmethod
    def default_department():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.department.id if employee else None

    @staticmethod
    def default_pay_in_band():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.pay_in_band if employee else None

    @classmethod
    def calculate_instalment(cls, records):
        for record in records:
            if record.check == False:
                cls.loan_installment(records)
                record.check = True
                record.save()

    @classmethod
    @ModelView.button
    @Workflow.transition('forwarded_to_jo')
    def submitted_to_jo(cls, records):
        """Change status of loan application to forwarded_to_jo"""
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('forwarded_to_ao')
    def forward_to_jo(cls, records):
        """Change status of loan application to forwarded_to_ao"""
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approve')
    def forward_to_ao(cls, records):
        """Change status of loan application to approve"""
        for record in records:
            record.set_approvedby()

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        """Change status of loan application to cancel"""
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
            self.pay_in_band = self.employee.pay_in_band
            pool = Pool()
            hrcontract = pool.get('hr.contract')
            contracts = hrcontract.search([
                ('employee', '=', self.employee)
            ])
            for contract in contracts:
                self.basic_pay = contract.basic
            loan = pool.get('computer.loan')
            loans = loan.search([
                ('employee', '=', self.employee)
            ])
            interest = 0
            for computer_loan in loans:
                for line in computer_loan.loan_line:
                    if line.status != 'done':
                        interest += line.amount
                if interest > 0:
                    self.purpose = 'yes'
                    self.drawal_date = computer_loan.approve_date
                    self.interest = interest
                else:
                    self.purpose = 'no'

    @classmethod
    def write(cls, *args):
        """ Override default write method of model """
        actions = iter(args)
        for mechanisms, values in zip(actions, actions):
            if 'installment_no' in values.keys() or 'amount_required' in values.keys() or 'price' in values.keys():
                cls.change_loan_installment(mechanisms, values)
        super(ComputerLoan, cls).write(*args)

    @classmethod
    def change_loan_installment(cls, records, values):
        """Change number of installments pending for loan"""
        cursor = Transaction().connection.cursor()
        LoanLine = Pool().get('computer.loan.line')
        amount = 0
        for loan in records:
            cursor.execute('SELECT sum(amount) FROM computer_loan_line \
                WHERE loan=%s AND status = %s', (loan.id, 'done'))
            total_amount = cursor.fetchone()
            if total_amount[0]:
                amount_value = min(loan.amount_required, loan.price)
                reschedule = amount_value - total_amount[0]
                cls.write(records, {'payout': total_amount[0],
                                    'reschedule': reschedule})
                amount = (reschedule/values['installment_no'])
            else:
                if 'installment_no' in values.keys():
                    amount_value = min(loan.amount_required, loan.price)
                    amount = (amount_value/values['installment_no'])
                elif 'amount_required' in values.keys():
                    amount_value = min(values['amount_required'], loan.price)
                    amount = (amount_value/loan.installment_no)
                elif 'price' in values.keys():
                    amount_value = min(loan.amount_required, values['price'])
                    amount = (amount_value/loan.installment_no)
                elif 'installment_no' in values.keys() and 'price' in values.keys() and 'amount_required' in values.keys():
                    amount_value = min(
                        values['amount_required'], values['price'])
                    amount = (amount_value/values['installment_no'])
                elif 'installment_no' in values.keys() and 'price' in values.keys():
                    amount_value = min(loan.amount_required, values['price'])
                    amount = (amount_value/values['installment_no'])
                elif 'installment_no' in values.keys() and 'amount_required' in values.keys():
                    amount_value = min(values['amount_required'], loan.price)
                    amount = (amount_value/values['installment_no'])
                elif 'price' in values.keys() and 'amount_required' in values.keys():
                    amount_value = min(
                        values['amount_required'],  values['price'])
                    amount = (amount_value/loan.installment_no)
            cursor.execute('delete FROM computer_loan_line WHERE loan=%s \
            AND status != %s', (loan.id, 'done'))
            count = 0
            installment_no = 0
            if 'installment_no' in values.keys():
                installment_no = values['installment_no']
            else:
                installment_no = loan.installment_no
            for line in range(1, int(installment_no)+1):
                mydate = datetime.now().month
                if total_amount[0]:
                    month = mydate
                else:
                    month = mydate - 1
                if month+line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime(1900, count, 1).date().strftime('%B')
                else:
                    months = datetime(1900, month+line,
                                      1).date().strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'loan': loan.id
                }
                line = LoanLine.create([vals])

    @classmethod
    def loan_installment(cls, records):
        """Calculate number of installments for loan"""
        count = 0
        LoanLine = Pool().get('computer.loan.line')
        for loan in records:
            amount_value = min(loan.amount_required, loan.price)
            amount = (amount_value/loan.installment_no)
            for line in range(1, int(loan.installment_no)+1):
                mydate = datetime.now().month
                month = mydate - 1
                if month + line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime(1900, count, 1).date().strftime('%B')
                else:
                    months = datetime(1900, month+line,
                                      1).date().strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'loan': loan.id
                }
                line = LoanLine.create([vals])

    def set_approvedby(self):
        '''
        Fill the approved by and approve date field
        '''
        approve_date = datetime.now().date()
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        self.approve_date = approve_date
        self.approve_by = user.id
        self.save()


class LoanCancelreason(ModelSQL, ModelView):
    'Loan Cancel Reason'

    __name__ = 'loan.cancel.reason'
    _rec_name = 'name'

    name = fields.Char("Cancel Reason")


class ComputerloanLine(ModelSQL, ModelView):
    'Computer loan Lines'

    __name__ = 'computer.loan.line'
    _rec_name = 'month'

    month = fields.Char("Month")
    amount = fields.Float("Amount")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('inprogress', 'Inprogress'),
        ('done', 'Done'),
    ], string='Status',)
    loan = fields.Many2One("computer.loan", "Loan")

    @staticmethod
    def default_status():
        return 'pending'
