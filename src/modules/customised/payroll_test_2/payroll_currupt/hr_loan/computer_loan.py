import datetime
from trytond.model import Workflow
from trytond.model import (
    ModelView, ModelSQL, fields)
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction

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
    designation = fields.Many2One("employee.designation",
        "Applicant's Designation",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    department = fields.Many2One('company.department', 'Department',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    pay_in_band = fields.Char('Pay in the Pay Band',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    price = fields.Float('Price of Personal Computer',
        required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    amount_required = fields.Float("Amount Required",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    date_of_retirement = fields.Date('Date of Retirement',
        required=True,
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    dob = fields.Date("Date of Birth",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    installment_no = fields.Integer("Number of installment",
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
    cancel_reason = fields.Many2One('loan.cancel.reason', 'Cancel Reason',
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
    pending = fields.Float('Pending',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('refund').in_(['refundable']),
        }, depends=['state'])
    reschedule = fields.Float('Reschedule',
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
            'readonly': ~Eval('state').in_(['approve']),
            'invisible': ~Eval('state').in_(['approve'])
        }, depends=['state'])
    approve_by = fields.Many2One('res.user', 'Approved By',
        states={
            'readonly': ~Eval('state').in_(['approve']),
            'invisible': ~Eval('state').in_(['approve'])
        }, depends=['state'])
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('forwarded_to_jo', 'Forwarded to JO'),
            ('forwarded_to_ao', 'Forwarded to AO'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
        ], 'Status', readonly=True
    )

    @classmethod
    def validate(cls, records):
        """Method to validate records(rows) in a model(table)"""
        
        super(ComputerLoan, cls).validate(records)
        for record in records:
            if record.price < record.amount_required:
                cls.raise_user_error('Computer price less then required amount')

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
        """Change status of loan application to forwarded_to_jo"""
        cls.loan_installment(records)
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
        cls.set_approvedby(records)
        pass

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
                ('employee', '=', self.employee),
                ('active', '<=', True)
                ])
            for contract in contracts:
                self.basic_pay = contract.basic

    @classmethod
    def write(cls, *args):
        """ Override default write method of model """
        actions = iter(args)
        for mechanisms, values in zip(actions, actions):
            if  'installment_no' in values.keys():
                cls.change_loan_installment(mechanisms, values)
        super(ComputerLoan, cls).write(*args)

    @classmethod
    def change_loan_installment(cls, records, values):
        """Change number of installments pending for loan"""
        cursor = Transaction().connection.cursor()
        LoanLine = Pool().get('computer.loan.line')
        for loan in records:
            cursor.execute('SELECT sum(amount) FROM computer_loan_line WHERE loan=%s \
                AND status = %s', (loan.id, 'done'))
            total_amount = cursor.fetchone()
            if total_amount[0]:
                reschedule = loan.amount_required - total_amount[0]
                cls.write(records, {'payout': total_amount[0],
                                    'reschedule': reschedule})
                amount = (reschedule/values['installment_no'])
            else:
                amount = (loan.amount_required/values['installment_no'])
            cursor.execute('delete FROM computer_loan_line WHERE loan=%s \
            AND status != %s', (loan.id, 'done'))
            count = 0
            for line in range(1, int(values['installment_no'])+1):
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
                    'loan': loan.id
                }
                line = LoanLine.create([vals])

    @classmethod
    def loan_installment(cls, records):
        """Calculate number of installments for loan"""
        count = 0
        LoanLine = Pool().get('computer.loan.line')
        for loan in records:
            amount = (loan.amount_required/loan.installment_no)
            for line in range(1, int(loan.installment_no)+1):
                mydate = datetime.datetime.now().month
                month = mydate - 1
                if month + line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime.date(1900, count, 1).strftime('%B')
                else:
                    months = datetime.date(1900, month+line, 1).strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'loan': loan.id
                }
                line = LoanLine.create([vals])

    @classmethod
    def set_approvedby(cls, computerloan):
        '''
        Fill the approved by and approve date field
        '''
        approve_date = datetime.datetime.now().date()
        for loan in computerloan:
            pool = Pool()
            User = pool.get('res.user')
            user = User(Transaction().user)
            print(approve_date, "approve_date", user.id,"fdsfhsdgfjhgsdf", loan.date_of_retirement)
            loan.approve_date = approve_date
            loan.approve_by = user.id
        cls.save(computerloan)

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
        ('done', 'Done'),
    ], string='Status',)
    loan = fields.Many2One("computer.loan", "Loan")

    @staticmethod
    def default_status():
        return 'pending'
