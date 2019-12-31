from datetime import datetime
from trytond.model import Workflow
from trytond.model import (
    ModelView, ModelSQL, fields)
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = ['HouseBuildingLoan', 'Construction', 'OwnHouse', 'HBAloanLine']


class HouseBuildingLoan(Workflow, ModelSQL, ModelView):
    'House Building Loan'
    __name__ = 'hba.loan'

    salary_code = fields.Char('Salary Code',
                              states={
                                  'readonly': ~Eval('state').in_(['draft']),
                              }, depends=['state'], required=True)
    employee = fields.Many2One('company.employee', 'Name of Applicant',
                               states={
                                   'readonly': ~Eval('state').in_(['draft']),
                               }, depends=['state'], required=True)
    designation = fields.Many2One(
        "employee.designation", "Designation",
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    department = fields.Many2One("company.department", "Department",
                                 states={
                                     'readonly': ~Eval('state').in_(['draft']),
                                 }, depends=['state'], required=True)
    post_held = fields.Selection([
        ('permanent', 'Permanent'),
        ('temporary_offg', 'Temporary/Offg'),
        ('length_of_service', 'Length of service on the date of application')
    ], string='Post held', sort=False,
        states={
        'readonly': ~Eval('state').in_(['draft']),
    }, depends=['state'], required=True)
    place_of_posting = fields.Char(
        'Place of Posting',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], required=True)
    scale_pay = fields.Char('Scale Pay',
                            states={
                                'readonly': ~Eval('state').in_(['draft']),
                            }, depends=['state'], required=True)
    pension_rule = fields.Selection([
        ('nps', 'NPS'),
        ('gpf', 'GPF'),
    ], string='Pension Rule', sort=False,
        states={
        'readonly': ~Eval('state').in_(['draft']),
    }, depends=['state'], required=True)
    retirement_date = fields.Date('Date of Retirement', required=True)
    advance = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],
        string='Any Other advance/Final withdrawal taken\
        for purchase of land/construction', sort=False,
        required=True)
    advance_needed = fields.Selection([
        ('plot', 'Purchase of Plot'),
        ('construction', 'Construction of new House'),
        ('enlarging_house', 'Enlarging existing House'),
        ('ready_built', 'Purchase of Ready Built House'),
        ('own_house', 'Own House')],
        string='Advance Needed for', sort=False,
        required=True)
    advance_amount = fields.Float(
        'Amount',
        states={
            'invisible': ~Eval('advance').in_(['yes']),
        }, depends=['advance'])
    source = fields.Char('Source',
                         states={
                             'invisible': ~Eval('advance').in_(['yes']),
                         }, depends=['advance'])
    attest_copy = fields.Many2One(
        'ir.attachment', 'attested Copy',
        states={
            'invisible': ~Eval('advance').in_(['yes']),
        }, depends=['advance'])
    location_address = fields.Char(
        'Location with Address',
        states={
            'invisible':
            ~Eval('advance_needed').in_(['plot', 'enlarging_house']),
        }, depends=['advance_needed'])
    location_type = fields.Selection([
        ('rural', 'Rural'),
        ('urbun', 'Urban'), ],
        string='Location Type', sort=False,
        states={
            'invisible': ~Eval('advance_needed').in_(['plot']),
    }, depends=['advance_needed'])
    clearly = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')],
        string='Is it Clearly Demacrated & Developed', sort=False,
        states={
            'invisible': ~Eval('advance_needed').in_(['plot']),
    }, depends=['advance_needed'])
    area = fields.Float('Apporximate area(in sq.mts.)',
                        states={
                            'invisible': ~Eval('advance_needed').in_(['plot']),
                        }, depends=['advance_needed'])
    cost = fields.Float('cost',
                        states={
                            'invisible': ~Eval('advance_needed').in_(['plot']),
                        }, depends=['advance_needed'])
    amount = fields.Float(
        'Amount actually paid',
        states={
            'invisible': ~Eval('advance_needed').in_(['plot']),
        }, depends=['advance_needed'])
    acquired = fields.Char(
        'If not Purchase when proposed to be acquired',
        states={
            'invisible': ~Eval('advance_needed').in_(['plot']),
        }, depends=['advance_needed'])
    unexpired = fields.Char(
        'Unexpired portion of lease if not free hold',
        states={
            'invisible': ~Eval('advance_needed').in_(['plot']),
        }, depends=['advance_needed'])
    amount_required = fields.Float('Amount of advance required', required=True)
    installment_no = fields.Integer(
        'No. of instalments for repayment', required=True)
    construction = fields.One2Many(
        'construction', 'hba_loan', 'Construction',
        states={
            'invisible': ~Eval('advance_needed').in_(['construction']),
        }, depends=['advance_needed'])
    floor = fields.Integer('Floor-wise area to be constructed')
    plinth_area = fields.Float('Plinth area(in sq.mtrs.')
    enlargement = fields.Float(
        'Plinth area proposed for enlargement(in sq. mtrs.)')
    cunstr_cost = fields.Float('Construction Cost')
    enlargement_cost = fields.Float('Cost of proposed enlargement')
    total_plinth = fields.Float('Total Plinth area')
    total_cost = fields.Float('Total Cost')
    constructed = fields.Date('When Constructed')
    price_settled = fields.Float('Price Settled')
    agency = fields.Char('The Agency from whom to be purchased')
    already_paid = fields.Float('Already paid')
    to_be_paid = fields.Float('To be Paid')
    own_house = fields.One2Many(
        'own.house', 'hba_loan', 'Own House',
        states={
            'invisible': ~Eval('advance_needed').in_(['own_house']),
        }, depends=['advance_needed'])
    loan_line = fields.One2Many(
        'hba.loan.line', 'loan', 'Installment Lines',
        readonly=True)
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
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('forwarded_to_jo', 'Forwarded to JO'),
            ('forwarded_to_ao', 'Forwarded to AO'),
            ('approve', 'Approved'),
            ('cancel', 'Cancel')
        ], 'Status', readonly=True, sort=False
    )
    cancel_reason = fields.Char(
        'Cancel Reason',
        states={
            'invisible': ~Eval(
                'state').in_(['forwarded_to_ao', 'cancel']),
            'readonly': ~Eval('state').in_(['forwarded_to_ao']),
        }, depends=['state'],)
    check = fields.Boolean('Check',
                           states={
                               'invisible': Eval('state').in_(['draft', 'forwarded_to_ao', 'forwarded_to_jo', 'approve', 'cancel']),
                           }, depends=['state'])

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
        return employee.designation.id if employee.designation else None

    @staticmethod
    def default_department():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.department.id if employee.department else None

    @staticmethod
    def default_pay_in_band():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.pay_in_band if employee else None

    @staticmethod
    def default_pension_rule():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.gpf_nps if employee else None

    @classmethod
    def validate(cls, records):
        """Method to validate records(rows) in a model(table)"""
        super().validate(records)
        for record in records:
            house_loan = cls.search([
                ('id', '!=', record.id),
                ('employee', '=', record.employee),
                ('state', '=', 'approve')
            ])
            if house_loan:
                cls.raise_user_error(
                    'You have alraedy take house loan')

    @classmethod
    def view_attributes(cls):
        """Define states for attributes in form view"""
        plot = ~Eval('advance_needed').in_(['plot'])
        construction = ~Eval('advance_needed').in_(['construction'])
        enlarging_house = ~Eval('advance_needed').in_(['enlarging_house'])
        ready_built = ~Eval('advance_needed').in_(['ready_built'])
        own_house = ~Eval('advance_needed').in_(['own_house'])

        attribute = [
            ("//page[@id='plot']", "states", {"invisible": plot}),
            ("//page[@id='construction']",
             "states", {"invisible": construction}),
            ("//page[@id='existing_house']", "states",
             {"invisible": enlarging_house}),
            ("//page[@id='build_house']",
             "states", {"invisible": ready_built}),
            ("//page[@id='own_house']", "states", {"invisible": own_house}),
        ]
        return attribute

    @fields.depends('employee')
    def on_change_employee(self, name=None):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department
            self.pay_in_band = self.employee.pay_in_band
            if self.employee.gpf_nps:
                self.pension_rule = self.employee.gpf_nps

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

    @classmethod
    def loan_installment(cls, records):
        """Calculate number of installments for loan"""
        count = 0
        LoanLine = Pool().get('hba.loan.line')
        for loan in records:
            amount = (loan.amount_required/loan.installment_no)
            for line in range(1, int(loan.installment_no)+1):
                mydate = datetime.now().month
                month = mydate - 1
                if month + line > 12:
                    count += 1
                    if count > 12:
                        count = 1
                    months = datetime.now().date(1900, count, 1).strftime('%B')
                else:
                    months = datetime.now().date(1900, month+line, 1).strftime('%B')
                vals = {
                    'month': months,
                    'amount': amount,
                    'status': 'pending',
                    'loan': loan.id
                }
                line = LoanLine.create([vals])

    @classmethod
    def write(cls, *args):
        """ Override default write method of model """
        actions = iter(args)
        for mechanisms, values in zip(actions, actions):
            if 'installment_no' in values.keys() or 'amount_required' in values.keys():
                cls.change_loan_installment(mechanisms, values)
        super().write(*args)

    @classmethod
    def change_loan_installment(cls, records, values):
        """Change number of installments pending for loan"""
        cursor = Transaction().connection.cursor()
        LoanLine = Pool().get('hba.loan.line')
        amount = 0
        for loan in records:
            cursor.execute('SELECT sum(amount) FROM hba_loan_line \
                WHERE loan=%s AND status != %s', (loan.id, 'pending'))
            total_amount = cursor.fetchone()
            if total_amount[0]:
                reschedule = loan.amount_required - total_amount[0]
                cls.write(records, {'payout': total_amount[0],
                                    'reschedule': reschedule})
                amount = (reschedule/values['installment_no'])
            else:
                if 'installment_no' in values.keys():
                    amount = (loan.amount_required/values['installment_no'])
                elif 'amount_required' in values.keys():
                    amount = (values['amount_required']/loan.installment_no)
                elif 'installment_no' in values.keys() and 'amount_required' in values.keys():
                    amount = (values['amount_required'] /
                              values['installment_no'])
            cursor.execute('delete FROM hba_loan_line WHERE loan=%s \
            AND status = %s', (loan.id, 'pending'))
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


class Construction(ModelSQL, ModelView):
    'Construction'
    __name__ = 'construction'

    floor_no = fields.Integer('Floor No.')
    location_address = fields.Char('Location with Address')
    location_type = fields.Selection([
        ('rural', 'Rural'),
        ('urbun', 'Urban'), ],
        string='Location Type', sort=False)
    floor_constructed = fields.Float('Floor-wise area to be constructed')
    estimated_cost = fields.Float('Estimated Cost')
    hba_loan = fields.Many2One('hba.loan', 'HBA Loan')


class OwnHouse(ModelSQL, ModelView):
    'Own House'
    __name__ = 'own.house'

    location_address = fields.Char('Location with Address')
    plinth_area = fields.Float('Plinth area(Floor-wise)')
    fair = fields.Float('Present fair market value')
    reasons = fields.Char(
        'Reasons for acquiring another house of enlarging existing house')
    hba_loan = fields.Many2One('hba.loan', 'HBA Loan')


class HBAloanLine(ModelSQL, ModelView):
    'HBA loan Lines'

    __name__ = 'hba.loan.line'
    _rec_name = 'month'

    month = fields.Char("Month")
    amount = fields.Float("Amount")
    status = fields.Selection([
        ('pending', 'Pending'),
        ('inprogress', 'Inprogress'),
        ('done', 'Done'),
    ], string='Status',)
    loan = fields.Many2One("hba.loan", "Loan")

    @staticmethod
    def default_status():
        return 'pending'
