from datetime import datetime, date
from trytond.model import ModelView, ModelSQL, fields, Workflow
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'RenumerationBill', 'TADABill', 'TADAJourney',
    'TADAHotelFood', 'TADALocalTransport', 'ContingencyBill',
    'ContingencyJourney', 'TADAllowancePerDay',
    'TADAHotelFoodEntitlement', 'RenumerationPurposeandPay'
]

class RenumerationBill(Workflow, ModelSQL, ModelView):
    '''Examination Renumeration Bill'''

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
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], 'Status', readonly=True)
    type_of_examiner = fields.Selection([
        ('internal', 'Internal'),
        ('external', 'External')
        ], 'Type of Examiner',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state']
    )
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
    
    exam = fields.Many2One('exam_section.exam', 'Exam', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
    )
    course_name = fields.Char('Name of Course', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state']
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
    total_amount = fields.Function(
        fields.Float('Total Amount'),
        'get_total_amount')
    net_amount = fields.Function(
        fields.Float(
            'Net Amount',
            help='Less student benevolent fund(5%) deducted for AIIMS employee'
        ),
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

    @staticmethod
    def default_state():
        return 'draft'
    
    @fields.depends('employee')
    def on_change_with_designation(self):
        '''Fill up employee designation field 
           as soon as employee field is changed'''
        if self.employee:
            if self.employee.designation:
                return self.employee.designation.name
    
    def get_total_amount(self, name):
        '''Calculate total amount of Renumeration Bill'''
        res = 0
        if self.purpose:
            for purpose in self.purpose:
                res += purpose.amount
        return res

    def get_net_amount(self, name):
        '''Calculate net amount of Renumeration Bill
           (5% is deducted for AIIMS Employee which goes
           to less student benevolent fund)'''
        res = 0
        total_amount = self.total_amount
        if self.type_of_examiner == 'internal':
            res = 0.95 * (total_amount)
        else:
            res = total_amount
        return res
    
    @classmethod
    def __setup__(cls):
        '''Setup error messages, workflow transitions, and button properties
           when an instance of this class is initialized'''
        super().__setup__()
        cls._error_messages.update({
            'submitted_bill':
                'A Submitted Bill can not be deleted'
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

    '''Button functions for executing workflow transitions
       (except delete)'''
    @classmethod
    @Workflow.transition('confirm')
    def confirm_data(cls,records):
        '''Change status of bill to confirm'''
        pass
    
    @classmethod
    @Workflow.transition('aao_approval')
    def send_for_aao_approval(cls,records):
        '''Change status of bill to aao_approval'''
        pass

    @classmethod
    @Workflow.transition('ao_approval')
    def send_for_ao_approval(cls,records):
        '''Change status of bill to ao_approval'''
        pass

    @classmethod
    @Workflow.transition('ace_approval')
    def send_for_ace_approval(cls, records):
        '''Change status of bill to ace_approval'''
        pass

    @classmethod
    @Workflow.transition('adean_approval')
    def send_for_adean_approval(cls, records):
        '''Change status of bill to adean_approval'''
        pass

    @classmethod
    @Workflow.transition('dean_approval')
    def send_for_dean_approval(cls, records):
        '''Change status of bill to dean_approval'''
        pass

    @classmethod
    @Workflow.transition('ao_approval_2')
    def send_for_ao_approval_2(cls, records):
        '''Change status of bill to ao_approval_2'''
        pass

    @classmethod
    def delete(cls, records):
        '''Override delete to ensure that the submitted bills are not deleted.
        '''
        res = super().delete(records)
        for record in records:
            if record.state not in ('draft'):
                cls.raise_user_error('submitted_bill')
        return res


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
            'amt_lt_0': 'Amount is less than zero',
            'max_range': 'Maximum Amount exceeded',
        })
    
    @classmethod
    def validate(cls, records):
        super(RenumerationPurposeandPay, cls).validate(records)
        for record in records:
            record.check_amount()

    def check_amount(self):
        '''Check whether: 
                (i) amount is less thanm zero or not
                (ii) amount exceeds maximum amount 
                     allowed for spefific purpose or not'''
        amount = self.amount
        purpose = self.purpose
        if amount and purpose:
            if amount < 0:
                self.raise_user_error('amt_lt_0')
            elif purpose.max_range != 0 and amount > purpose.max_range:
                self.raise_user_error('max_range')

    # @classmethod
    # def show_exam_type(cls, records):
    #     for rec in records:
    #         print(rec.renumeration.exam.exam_type)
    
    @fields.depends('renumeration')
    def on_change_with_external(self, name=None):
        '''Function for hidden field to determine whether bill 
           is for AIIMS Employee or external examiner'''
        if self.renumeration:
            if self.renumeration.type_of_examiner == 'external':
                return True
        return False
    
    @fields.depends('renumeration')
    def on_change_with_exam_type(self, name=None):
        '''Function for hidden field to fetch type of examination'''
        if self.renumeration and self.renumeration.exam:
            return self.renumeration.exam.exam_type.id
    
    @fields.depends('purpose')
    def on_change_with_payment_basis(self):
        '''Function for fetching payment basis
           (Daily, Hourly, Per Session, Per Copy, Per Exam)'''
        if self.purpose.payment_basis:
            return self.purpose.payment_basis.name

    @fields.depends('purpose', 'renumeration')
    def calculate_amount_payable(self, name):
        '''Calculate total amount for Renumeration Bill'''
        res = 0
        if self.purpose and self.unit:
            res = self.unit * self.purpose.type_amount_fix
            if self.purpose.min_range and res < self.purpose.min_range:
                res = self.purpose.min_range
        return res

class TADABill(Workflow, ModelSQL, ModelView):
    '''Examination TA/DA Bill'''

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
    center = fields.Many2One('exam.centers', 'Center')
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
    recovery = fields.Function(
        fields.Float('Recovery'),
        'calculate_recovery'
    )
    net_paid = fields.Function(
        fields.Float('Net Paid'),
        'calculate_net_paid'
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
    

    @property
    def total_hotel_amount(self):
        res = 0
        if self.hotel_food:
            for record in self.hotel_food:
                if record.type_ in ['hotel']:
                    res += record.amount
        return res

    @property
    def total_food_amount(self):
        res = 0
        if self.hotel_food:
            for record in self.hotel_food:
                if record.type_ in ['food']:
                    res += record.amount
        return res

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def __setup__(cls):
        '''Setup workflow transitions and button properties
           when an instance of this class is initialized'''
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
        '''Calculate the total amount for journey 
           entered in TA/DA Bill by employee'''
        total = 0
        if self.journey:
            for journey in self.journey:
                total += journey.amount
        return total
    
    def get_total_hotel_food_amount(self, name):
        '''Calculate the total amount for hotel and food 
           entered in TA/DA Bill by employee'''
        total = 0
        if self.hotel_food:
            for record in self.hotel_food:
                total += record.amount
        return total

    def get_total_local_transport_amount(self, name):
        '''Calculate the total amount for hotel and food 
           entered in Hotel/Food section of TA/DA Bill by employee'''
        total = 0
        if self.local_transport:
            for record in self.local_transport:
                total += record.amount
        return total
    
    def get_total_amount(self, name):
        '''Calculate the total amount of TA/DA Bill'''
        return (self.total_journey + self.total_hotel_food + self.total_local_transport)

    def calculate_recovery(self, name):
        '''Calculate the recovery for hotel stay, food and journey 
           entered in TA/DA Bill by employee'''
        global days_hotel
        global days_food
        global hotel_entitlement
        global food_entitlement
        days_hotel = 0
        days_food = 0
        hotel_entitlement = 0
        food_entitlement = 0
        res = 0
        ta_da_lines = self.exam.exam_type.ta_da
        employee_grade_pay = float(self.employee.grade_pay.name)
        for line in ta_da_lines:
            if self.employee.employee_group == line.group:
                for grade_pay in line.grade_pays:
                    if employee_grade_pay >= float(grade_pay.grade_pay.name):
                        hotel_entitlement = line.hotel_charges
                        food_entitlement = line.food_charges
        for hotel_food in self.hotel_food:
            days_hotel += hotel_food.no_of_nights_stayed \
                        if hotel_food.type_ in ['hotel'] else 0 
            days_food += hotel_food.no_of_days_food \
                        if hotel_food.type_ in ['food'] else 0
        total_hotel = days_hotel * hotel_entitlement
        total_food = days_food * food_entitlement
        hotel_amount = self.total_hotel_amount
        food_amount = self.total_food_amount
        recovery_hotel = total_hotel - hotel_amount \
                        if total_hotel > hotel_amount else 0
        recovery_food = total_food - food_amount \
                        if total_food > food_amount else 0
        res = recovery_food + recovery_hotel
        return res
    
    
    def calculate_net_paid(self, name):
        '''Calculate net paid amount, i.e.
           total amount - recovery amount'''
        return self.total_amount - self.recovery
    
    @property
    def total_hotel_amount(self):
        '''Calculate the total amount for hotel stay entered in
           Hotel/Food section of TA/DA Bill by employee'''
        res = 0
        if self.hotel_food:
            for record in self.hotel_food:
                if record.type_ in ['hotel']:
                    res += record.amount
        return res

    @property
    def total_food_amount(self):
        '''Calculate the total amount for food entries entered in
           Hotel/Food section of TA/DA Bill by employee'''
        res = 0
        if self.hotel_food:
            for record in self.hotel_food:
                if record.type_ in ['food']:
                    res += record.amount
        return res
    
    @classmethod
    @Workflow.transition('confirm')
    def submit(cls, records):
        '''Change status of bill to confirm
           Set submit date when TA/DA Bill is submitted'''
        for record in records:
            record.submit_date = date.today()
            record.save()

    '''Button functions for executing workflow transitions'''
    @classmethod
    @Workflow.transition('aao_approval')
    def send_for_aao_approval(cls,records):
        '''Change status of bill to aao_approval'''
        pass

    @classmethod
    @Workflow.transition('ao_approval')
    def send_for_ao_approval(cls,records):
        '''Change status of bill to ao_approval'''
        pass

    @classmethod
    @Workflow.transition('ace_approval')
    def send_for_ace_approval(cls, records):
        '''Change status of bill to ace_approval'''
        pass

    @classmethod
    @Workflow.transition('adean_approval')
    def send_for_adean_approval(cls, records):
        '''Change status of bill to adean_approval'''
        pass

    @classmethod
    @Workflow.transition('dean_approval')
    def send_for_dean_approval(cls, records):
        '''Change status of bill to dean_approval'''
        pass

    @classmethod
    @Workflow.transition('ao_approval_2')
    def send_for_ao_approval_2(cls, records):
        '''Change status of bill to ao_approval_2'''
        pass

    @classmethod
    @Workflow.transition('approved')
    def approve(cls, records):
        '''Set approved date when TA/DA Bill is approved'''
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
        '''Check whether departure date is greater than 
           arrival date or not'''
        if self.departure_date > self.arrival_date:
            self.raise_user_error('date_error')

    def check_amount(self):
        '''Check whether amount is less than zero or not'''
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
        '''Calculate number of nights stayed in hotel using from_date
           and to_date'''
        if self.type_ == 'hotel':
            if self.from_date:
                if self.to_date:
                    no_of_days_delta = self.to_date - self.from_date 
                    return int(no_of_days_delta.days)
        return 0

    @fields.depends('from_date', 'to_date', 'type_')
    def on_change_with_no_of_days_food(self):
        '''Calculate number of days of food consumption using from_date
           and to_date'''
        if self.type_ == 'food':
            if self.from_date:
                if self.to_date:
                    no_of_days_delta = self.to_date - self.from_date 
                    return int(no_of_days_delta.days)
        return 0

    @classmethod
    def validate(cls, records):
        super(TADAHotelFood, cls).validate(records)
        for record in records:
            record.check_date()
            record.check_amount()

    def check_date(self):
        '''Check whether from_date is greater than to_date or not'''
        if self.from_date > self.to_date:
            self.raise_user_error('date_error')

    def check_amount(self):
        '''Check whether amount is less than zero or not'''
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
    amount = fields.Function(
        fields.Float('Amount'),
        'on_change_with_amount'
    )
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

    @fields.depends('km')
    def on_change_with_amount(self, name=None):
        '''Calculate amount based on kilometers travelled'''
        res = 0
        if self.km:
            res = self.km * 16
        return res

    def check_amount(self):
        '''Check whether amount is less than zero or not'''
        if self.amount < 0:
            self.raise_user_error('amount_lt_0')


class ContingencyBill(ModelSQL, ModelView):
    '''Examination Contingency Bill'''

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
        '''Calculate total distance travelled'''
        res = 0
        for journey in self.journey:
            res += journey.journey_distance
        return res

    def get_total_amount(self, name):
        '''Calculate total amount'''
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


