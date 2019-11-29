from datetime import datetime, date
from trytond.model import ModelView, ModelSQL, fields, Workflow
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'RenumerationBill', 'TADABill', 'TADAJourney',
    'TADAHotelFood', 'TADALocalTransport', 'ContingencyBill',
    'ContingencyJourney', 'RenumerationSignature',
    'TADASignature', 'TADAllowancePerDay',
    'TADAHotelFoodEntitlement', 'RenumerationPurposeandPay'
]

class RenumerationBill(ModelSQL, ModelView, Workflow):
    '''Renumeration Bill'''

    __name__ = 'exam_section.renumeration_bill'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('aao_approval', 'AAO Approval'),
        ('ao_approval', 'AO Approval'),
        ('ace_approval', 'ACE Approval'),
        ('adean_approval', 'Assistant Dean Approval'),
        ('dean_approval', 'Dean Approval'),
        ('ao_approval_2', 'AO Approval 2'),
        ('salary_release', 'Salary Release'),
        ('rejected', 'Rejected')
    ], 'Status', readonly=True)
    type_of_examiner = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
        ],
        'Type of Examiner',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee', states={
        'invisible': Eval('type_of_examiner') == 'external',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'],)

    examiner_name = fields.Char('Name of Examiner', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])

    designation = fields.Char('Designation', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])

    address = fields.Text('Address', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])

    pincode = fields.Integer('Pin Code', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])
    
    exam = fields.Many2One(
        'exam_section.exam',
        'Exam',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        },
        depends=['state']
    )
    course_name = fields.Char(
        'Name of Course',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        },
        depends=['state'])
    no_of_papers_set = fields.Integer(
        'Number of papers set',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('exam.exam_type.type_exam').in_(['ug'])
        },
        depends=['state'])
    papers_set_amount_payable = fields.Function(
        fields.Float('Amount Payable(Papers Set)'),
        'get_amount_papers_set',
        )
    no_of_ans_books_evaluated = fields.Integer(
        'No. of Answer Books Evaluated',
        )
    no_of_candidates = fields.Integer(
        'Number of candidates',
    )
    purpose = fields.One2Many(
        'exam_type.purpose_and_pay_renum',
        'renumeration',
        'Purpose',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        },
        depends=['state']
        )
    no_of_students_examined = fields.Integer(
        'Number of Students Examined',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('exam.exam_type.type_exam').in_(['ug'])
        },
        depends=['state', 'exam'])
    evaluation_amount_payable = fields.Function(
        fields.Float('Amount Payable(Evaluation)'),
        'get_amount_evaluation')
    total_amount = fields.Function(
        fields.Float('Total Amount'),
        'get_total_amount')
    net_amount = fields.Function(
        fields.Float('Net Amount'),
        'get_net_amount')
    bank_name = fields.Char('Bank Name', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])
    bank_address = fields.Char('Bank Address', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])
    account_number = fields.Char('Account Number', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])
    ifsc_code = fields.Char('IFSC Code', states={
        'invisible': Eval('type_of_examiner') == 'internal',
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['type_of_examiner', 'state'])
    signatures = fields.One2Many(
        'exam_section.renumeration_signature',
        'renumeration',
        'Signatures'
        )

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_no_of_papers_set():
        return 0

    @staticmethod
    def default_no_of_ans_books_evaluated():
        return 0
    
    @staticmethod
    def default_no_of_student_examined():
        return 0
    
    @fields.depends('employee')
    def on_change_with_designation(self):
        if self.employee:
            if self.employee.designation:
                return self.employee.designation.name
    
    def get_total_amount(self, name):
        res = 0
        if self.purpose:
            for purpose in self.purpose:
                res += purpose.amount
        return res

    def get_net_amount(self, name):
        res = 0
        total_amount = self.total_amount
        if self.type_of_examiner == 'internal':
            res = 0.95 * (total_amount)
        else:
            res = total_amount
        return res
    
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions = set((
            ('draft', 'confirm'),
            ('confirm', 'aao_approval'),
            ('aao_approval', 'ao_approval'),
            ('ao_approval', 'ace_approval'),
            ('ace_approval', 'adean_approval'),
            ('adean_approval', 'dean_approval'),
            ('dean_approval', 'ao_approval_2'),
            ('ao_approval_2', 'salary_release')
        ))
        cls._buttons.update({
            'confirm_data': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'send_for_aao_approval': {
                'invisible': ~Eval('state').in_(['confirm'])
            },
            'send_for_ao_approval': {
                'invisible': ~Eval('state').in_(['aao_approval'])
            },
            'send_for_ace_approval': {
                'invisible': ~Eval('state').in_(['ao_approval'])
            },
            'send_for_adean_approval': {
                'invisible': ~Eval('state').in_(['ace_approval'])
            },
            'send_for_dean_approval': {
                'invisible': ~Eval('state').in_(['adean_approval'])
            },
            'send_for_ao_approval_2': {
                'invisible': ~Eval('state').in_(['dean_approval'])
            },
        })

    @classmethod
    @Workflow.transition('confirm')
    def confirm_data(cls,records):
        pass
    
    @classmethod
    @Workflow.transition('aao_approval')
    def send_for_aao_approval(cls,records):
        pass

    @classmethod
    @Workflow.transition('ao_approval')
    def send_for_ao_approval(cls,records):
        pass

    @classmethod
    @Workflow.transition('ace_approval')
    def send_for_ace_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('adean_approval')
    def send_for_adean_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('dean_approval')
    def send_for_dean_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('ao_approval_2')
    def send_for_ao_approval_2(cls, records):
        pass


class RenumerationPurposeandPay(ModelSQL, ModelView):
    '''Renumeration Purpose and Pay'''

    __name__ = 'exam_type.purpose_and_pay_renum'

    renumeration = fields.Many2One(
        'exam_section.renumeration_bill',
        'Renumeration Bill')
    exam_type = fields.Function(
        fields.Many2One(
            'exam_section.exam_type',
            'Exam Type'
        ),
        'on_change_with_exam_type'
    )
    external = fields.Function(
        fields.Boolean('External'),
        'on_change_with_external'
    )
    payment_basis = fields.Char('Payment Basis')
    unit = fields.Integer('Unit')
    purpose = fields.Many2One(
        'exam_section.exam_type.renumeration',
        'Purpose',
        domain=[
            ('exam_type', '=', Eval('exam_type')),
            ('is_external', '=', Eval('external'))
        ]
    )
    amount = fields.Function(
        fields.Float('Amount'),
        'calculate_amount_payable'
    )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'min_range': 'Minimum Amount not satisfied',
            'max_range': 'Maximum Amount exceeded',
        })
    
    @classmethod
    def validate(cls, records):
        super(RenumerationPurposeandPay, cls).validate(records)
        for record in records:
            record.check_amount()

    def check_amount(self):
        amount = self.amount
        purpose = self.purpose
        if amount and purpose:
            if amount < 0 or amount < purpose.min_range:
                self.raise_user_error('min_range')
            elif purpose.max_range != 0 and amount > purpose.max_range:
                self.raise_user_error('max_range')

    # @classmethod
    # def show_exam_type(cls, records):
    #     for rec in records:
    #         print(rec.renumeration.exam.exam_type)
    
    @fields.depends('renumeration')
    def on_change_with_external(self, name=None):
        if self.renumeration:
            if self.renumeration.type_of_examiner == 'external':
                return True
            else:
                return False
    
    @fields.depends('renumeration')
    def on_change_with_exam_type(self, name=None):
        if self.renumeration and self.renumeration.exam:
            return self.renumeration.exam.exam_type.id
    
    @fields.depends('purpose')
    def on_change_with_payment_basis(self):
        if self.purpose.payment_basis:
            return self.purpose.payment_basis.name

    @fields.depends('purpose', 'renumeration')
    def calculate_amount_payable(self, name):
        res = 0
        # import pdb; pdb.set_trace()
        if self.purpose and self.unit:
            res = self.unit * self.purpose.type_amount_fix
        return res

class TADABill(ModelSQL, ModelView, Workflow):
    '''TA/DA Bill'''

    __name__ = 'exam_section.ta_da_bill'

    employee = fields.Many2One('company.employee', 'Employee',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state']
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('aao_approval', 'AAO Approval'),
        ('ao_approval', 'AO Approval'),
        ('ace_approval', 'ACE Approval'),
        ('adean_approval', 'Assistant Dean Approval'),
        ('dean_approval', 'Dean Approval'),
        ('ao_approval_2', 'AO Approval 2'),
        ('approved', 'Approved')
        ], 'Status', readonly=True)
    submit_date = fields.Date('Submit Date', states={
        'readonly': ~Eval('state').in_([
            'draft', 'confirm',
        ])}
    )
    approved_date = fields.Date('Approved Date',
        states={
            'readonly': Eval('state').in_(['approved'])
        }
    )
    designation = fields.Many2One('employee.designation', 'Designation',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state']
    )
    department = fields.Many2One(
        'company.department',
        'Department',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
    )
    purpose = fields.Char(
        'Purpose of travel',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'],
        required=True
    )
    journey = fields.One2Many(
        'exam_section.ta_da.journey',
        'ta_da',
        'Journey',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
        )
    hotel_food = fields.One2Many(
        'exam_section.ta_da.hotel_food',
        'ta_da',
        'Hotel/Food',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    local_transport = fields.One2Many(
        'exam_section.ta_da.local_transport',
        'ta_da',
        'Local Transport',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
        )
    total_journey = fields.Function(
        fields.Float('Total Journey Amount'),
        'get_total_journey_amount'
    )
    total_hotel_food = fields.Function(
        fields.Float('Total Hotel/Food Amount'),
        'get_total_hotel_food_amount'
    )
    total_local_transport = fields.Function(
        fields.Float('Total Local Transport Amount'),
        'get_total_local_transport_amount'
    )
    total_amount = fields.Function(
        fields.Float('Total Amount'),
        'get_total_amount'
    )
    # signatures = fields.One2Many(
    #     'exam_section.ta_da_signature',
    #     'ta_da',
    #     'Signature',
    #     states={
    #         'readonly': ~Eval('state').in_(['draft'])
    #     },
    #     depends=['state']
    # )
    exam = fields.Many2One(
        'exam_section.exam',
        'Exam',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'],
        required=True
    )

    # @fields.depends('employee')
    # def on_change_with_designation(self):
    #     return self.employee.designation.name if self.employee else ''

    # @fields.depends('employee')
    # def on_change_with_department(self):
    #     return self.employee.department.name if self.employee else ''
    

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'submit': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'send_for_aao_approval': {
                'invisible': ~Eval('state').in_(['confirm'])
            },
            'send_for_ao_approval': {
                'invisible': ~Eval('state').in_(['aao_approval'])
            },
            'send_for_ace_approval': {
                'invisible': ~Eval('state').in_(['ao_approval'])
            },
            'send_for_adean_approval': {
                'invisible': ~Eval('state').in_(['ace_approval'])
            },
            'send_for_dean_approval': {
                'invisible': ~Eval('state').in_(['adean_approval'])
            },
            'send_for_ao_approval_2': {
                'invisible': ~Eval('state').in_(['dean_approval'])
            },
            'approve': {
                'invisible': ~Eval('state').in_(['ao_approval_2'])
            }
        })
        cls._transitions = set((
            ('draft', 'confirm'),
            ('confirm', 'aao_approval'),
            ('aao_approval', 'ao_approval'),
            ('ao_approval', 'ace_approval'),
            ('ace_approval', 'adean_approval'),
            ('adean_approval', 'dean_approval'),
            ('dean_approval', 'ao_approval_2'),
            ('ao_approval_2', 'approved')
        ))

    def get_total_journey_amount(self, name):
        total = 0
        if self.journey:
            for journey in self.journey:
                total += journey.amount
        return total
    
    def get_total_hotel_food_amount(self, name):
        total = 0
        if self.hotel_food:
            for record in self.hotel_food:
                total += record.amount
        return total

    def get_total_local_transport_amount(self, name):
        total = 0
        if self.local_transport:
            for record in self.local_transport:
                total += record.amount
        return total
    
    def get_total_amount(self, name):
        return (self.total_journey + self.total_hotel_food + self.total_local_transport)

    @classmethod
    @Workflow.transition('confirm')
    def submit(cls, records):
        for record in records:
            record.submit_date = date.today()
            record.save()

    @classmethod
    @Workflow.transition('aao_approval')
    def send_for_aao_approval(cls,records):
        pass
        

    @classmethod
    @Workflow.transition('ao_approval')
    def send_for_ao_approval(cls,records):
        pass

    @classmethod
    @Workflow.transition('ace_approval')
    def send_for_ace_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('adean_approval')
    def send_for_adean_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('dean_approval')
    def send_for_dean_approval(cls, records):
        pass

    @classmethod
    @Workflow.transition('ao_approval_2')
    def send_for_ao_approval_2(cls, records):
        pass
    
    @classmethod
    @Workflow.transition('approved')
    def approve(cls, records):
        for record in records:
            record.approved_date = date.today()
            record.save()


class TADAJourney(ModelSQL, ModelView):
    '''TA/DA Journey'''

    __name__ = 'exam_section.ta_da.journey'

    ta_da = fields.Many2One('exam_section.ta_da_bill', 'TA/DA Bill')
    journey_type = fields.Selection(
        [
            ('forward', 'Forward'),
            ('return', 'Return')
        ],
        'Journey Type',
        required=True)
    mode_of_transport = fields.Selection(
        [
            ('air', 'Air'),
            ('rail', 'Rail'),
            ('road', 'Road')
        ],
        'Mode of Transport',
        required=True)
    departure_place = fields.Char(
        'Departure Place',
        required=True)
    departure_date = fields.Date(
        'Departure Date',
        required=True)
    departure_time = fields.Time('Departure Time', required=True)
    arrival_place = fields.Char('Arrival Place', required=True)
    arrival_date = fields.Date('Arrival Date', required=True)
    arrival_time = fields.Time('Arrival Time', required=True)
    amount = fields.Float(
        'Amount',
        required=True
    )

    @staticmethod
    def default_amount():
        return 0

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'date_error': 'From date is more than to date',
            'amount_lt_0': 'Amount cannot be less than 0'
        })

    @classmethod
    def validate(cls, records):
        super(TADAJourney, cls).validate(records)
        for record in records:
            record.check_date()
            record.check_amount()

    def check_date(self):
        if self.departure_date > self.arrival_date:
            self.raise_user_error('date_error')

    def check_amount(self):
        if self.amount < 0:
            self.raise_user_error('amount_lt_0')
        


class TADAHotelFood(ModelSQL, ModelView):
    '''TA/DA Hotel/Food'''

    __name__ = 'exam_section.ta_da.hotel_food'

    ta_da = fields.Many2One('exam_section.ta_da_bill', 'TA/DA Bill')
    type_ = fields.Selection(
        [
            ('hotel', 'Hotel'),
            ('food', 'Food')
        ],
        'Type',
        required=True)
    no_of_nights_stayed = fields.Integer(
        'No. of Nights Stayed',
        states={
            'readonly': ~Eval('type_').in_(['hotel']),
            'invisible': ~Eval('type_').in_(['hotel']),
        },
        depends=['type_'])
    no_of_days_food = fields.Integer(
        'No. of Days Food',
        states={
            'readonly': ~Eval('type_').in_(['food']),
            'invisible': ~Eval('type_').in_(['food']),
        },
        depends=['type_'])
    from_date = fields.Date(
        'From Date',
        required=True
    )
    to_date = fields.Date(
        'To Date',
        required=True
    )
    amount = fields.Float(
        'Amount',
        required=True
    )
    have_bill = fields.Boolean('Bill?')
    bill = fields.Many2One('ir.attachment', 'Bill', states={
        'invisible': Eval('have_bill') != '1',
        'required': Eval('have_bill') == '1',
    }, depends=['have_bill'])

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'date_error': 'From date is more than to date',
            'amount_lt_0': 'Amount cannot be less than 0'
        })

    @staticmethod
    def default_amount():
        return 0

    @fields.depends('from_date', 'to_date', 'type_')
    def on_change_with_no_of_nights_stayed(self):
        if self.type_ == 'hotel':
            if self.from_date:
                if self.to_date:
                    no_of_days_delta = self.to_date - self.from_date 
                    return int(no_of_days_delta.days)
        else:
            return 0

    @fields.depends('from_date', 'to_date', 'type_')
    def on_change_with_no_of_days_food(self):
        if self.type_ == 'food':
            if self.from_date:
                if self.to_date:
                    no_of_days_delta = self.to_date - self.from_date 
                    return int(no_of_days_delta.days)
        else:
            return 0

    @classmethod
    def validate(cls, records):
        super(TADAHotelFood, cls).validate(records)
        for record in records:
            record.check_date()
            record.check_amount()

    def check_date(self):
        if self.from_date > self.to_date:
            self.raise_user_error('date_error')

    def check_amount(self):
        if self.amount < 0:
            self.raise_user_error('amount_lt_0')


class TADALocalTransport(ModelSQL, ModelView):
    '''TA/DA Local Transport'''

    __name__ = 'exam_section.ta_da.local_transport'

    ta_da = fields.Many2One(
        'exam_section.ta_da_bill',
        'TA/DA Bill',
        required=True
    )
    mode = fields.Selection([
        ('public', 'Public'),
        ('private', 'Private')
    ], 'Mode of transport', required=True)
    from_ = fields.Char('From', required=True)
    to = fields.Char('To', required=True)
    km = fields.Float('km', required=True)
    amount = fields.Float('Amount', required=True)
    have_receipt = fields.Boolean('Receipt?')
    receipt = fields.Many2One('ir.attachment', 'Receipt', states={
        'invisible': Eval('have_receipt') != '1',
        'required': Eval('have_receipt') == '1',
    }, depends=['have_receipt'])

    @staticmethod
    def default_amount():
        return 0

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'amount_lt_0': 'Amount cannot be less than 0'
        })
    
    @classmethod
    def validate(cls, records):
        super(TADALocalTransport, cls).validate(records)
        for record in records:
            record.check_amount()

    def check_amount(self):
        if self.amount < 0:
            self.raise_user_error('amount_lt_0')


class ContingencyBill(ModelSQL, ModelView):
    '''Contingency Bill'''

    __name__ = 'exam_section.contingency_bill'
    exam_center = fields.Many2One('exam_section.exam_center', 'Exam Center')
    journey = fields.One2Many(
        'exam_section.contigency.journey',
        'contingency',
        'Journey'
        )
    journey_total_distance = fields.Function(
        fields.Float('Total Distance'),
        'get_total_distance')
    journey_total_amount = fields.Function(
        fields.Float('Total Amount'),
        'get_total_amount')
    employee = fields.Many2One('company.employee', 'Employee')
    date = fields.Date('Date')

    def get_total_distance(self, name):
        res = 0
        for journey in self.journey:
            res += journey.journey_distance
        return res

    def get_total_amount(self, name):
        res = 0
        for journey in self.journey:
            res += journey.journey_amount
        return res

    


class ContingencyJourney(ModelSQL, ModelView):
    '''Contingency Journey'''

    __name__ = 'exam_section.contingency.journey'

    contingency = fields.Many2One(
        'exam_section.contingency_bill',
        'Contingency'
        )
    date_time_journey = fields.DateTime('Date and Time of Journey')
    from_location = fields.Char('From')
    to_location = fields.Char('To')
    mode_of_journey = fields.Selection([
        ('air', 'Air'),
        ('rail', 'Rail'),
        ('road', 'Road')
    ], 'Mode of Transport')
    sharing = fields.Boolean('Sharing?')
    journey_distance = fields.Float('Distance (in km)')
    journey_amount = fields.Float('Amount')


class RenumerationSignature(ModelSQL, ModelView):
    '''Renumeration Signature'''

    __name__ = 'exam_section.renumeration_signature'

    signed_by_user = fields.Many2One('res.user', 'Signed By')
    signed_by_employee = fields.Many2One(
        'company.employee',
        'Signed By Employee'
        )
    signed_on = fields.DateTime('Signed On')
    note = fields.Text('Remarks')
    designation = fields.Many2One(
        'employee.designation',
        'Designation'
        )
    place = fields.Char('Place')
    renumeration = fields.Many2One(
        'exam_section.renumeration_bill',
        'Renumeration Bill'
        )


class TADASignature(ModelSQL, ModelView):
    '''TA/DA Signature'''

    __name__ = 'exam_section.ta_da_signature'

    signed_by_user = fields.Many2One('res.user', 'Signed By')
    signed_by_employee = fields.Many2One(
        'company.employee',
        'Signed By Employee'
        )
    signed_on = fields.DateTime('Signed On')
    note = fields.Text('Remarks')
    designation = fields.Many2One(
        'employee.designation',
        'Designation'
        )
    place = fields.Char('Place')
    ta_da = fields.Many2One(
        'exam_section.ta_da_bill',
        'TA/DA Bill'
        )


class TADAllowancePerDay(ModelSQL, ModelView):
    '''TA/DA Allowance Per Day'''

    __name__ = 'exam_section.ta_da.allowance_per_day'

    group = fields.Char('Group')
    rate = fields.Float('Rate')


class TADAHotelFoodEntitlement(ModelSQL, ModelView):
    '''TA/DA Hotel/Food Entitlement'''

    __name__ = 'ta_da.hotel_food_entitlement'

    group = fields.Char('Group')
    pay_level = fields.Char('Pay Level')
    hotel_charges = fields.Float('Hotel Charges')
    food_charges = fields.Float('Food Charges')


