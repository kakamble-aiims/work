from datetime import date
from trytond.model import ModelView, ModelSQL, fields, Workflow, Unique
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'ExamCenter', 'ExamCenterAddress', 'Exam', 'Centers', 'Employees'
    ]


class ExamCenter(ModelSQL, ModelView):
    '''Exam Center'''

    __name__ = 'exam_section.exam_center'

    state = fields.Many2One(
        'country.subdivision',
        'State',
        domain=[('country.name', '=', 'India')]
        )
    name = fields.Char('City')
    code = fields.Char('Code', required="True")
    centers = fields.One2Many(
        'exam_section.exam_center.address', 'center', 'Centers'
    )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.__repr__ = 'code'


class ExamCenterAddress(ModelSQL, ModelView):
    '''Exam Center'''

    __name__ = 'exam_section.exam_center.address'

    center = fields.Many2One('exam_section.exam_center', 'Center')
    code = fields.Char('Code', required="True")
    name = fields.Text('Address')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.__repr__ = 'code'


class Exam(Workflow, ModelSQL, ModelView):
    '''Exam'''

    __name__ = 'exam_section.exam'

    _RENUM_PAGE_STATES = {
        'readonly': ~Eval('state').in_(['draft']),
        'invisible': Eval('state').in_([
            'draft',
            'confirm',
        ])
    }

    _TA_DA_PAGE_STATES = {
        'readonly': ~Eval('state').in_(['draft']),
        'invisible': Eval('state').in_([
            'draft',
            'confirm',
            'approved',
            'in_progress'
        ])
    }

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('awaiting_ta_da', 'Awaiiting TA/DA Bills'),
        ('ta_da_submit', 'TA/DA Submit'),
        ('aao_approval', 'AAO Approval'),
        ('ao_approval', 'AO Approval'),
        ('ace_approval', 'ACE Approval'),
        ('adean_approval', 'Assistant Dean Approval'),
        ('dean_approval', 'Dean Approval'),
        ('ao_approval_2', 'AO Approval 2'),
        ('approval', 'Approval'),
        ('budget_allocation', 'Budget Allocation'),
        ('final_process', 'Final Process')
    ], 'Status', readonly=True)
    name = fields.Char('Exam Name')
    exam_type = fields.Many2One(
        'exam_section.exam_type',
        'Exam Type',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'],
        required=True)
    date_from = fields.Date('Date From', states={
            'readonly': ~Eval('state').in_(['draft'])
            }, depends=['state'], required=True)
    date_to = fields.Date('Date To', states={
            'readonly': ~Eval('state').in_(['draft'])
            }, depends=['state'], required=True)
    centers = fields.One2Many('exam.centers', 'exam', 'Centers', states={
            'readonly': ~Eval('state').in_(['draft'])
            }, depends=['state'])
    employees = fields.One2Many('exam.employees', 'exam', 'Employees', states={
            'readonly': ~Eval('state').in_(['draft'])
            }, depends=['state'])
    renumeration_bills = fields.One2Many(
        'exam_section.renumeration_bill',
        'exam',
        'Renumeration Bills',
        states=_RENUM_PAGE_STATES,
        depends=['state']
    )
    ta_da_bills = fields.One2Many(
        'exam_section.ta_da_bill',
        'exam',
        'TA/DA Bills',
        states=_TA_DA_PAGE_STATES,
        depends=['state']
    )
    contingency_bills = fields.One2Many(
        'exam_section.contingency_bill',
        'exam',
        'Contingency Bills',
        states=_TA_DA_PAGE_STATES,
        depends=['state']
    )
    total_renumeration_cost = fields.Function(
        fields.Float('Total Renumeration Cost'),
        'get_total_renumeration')
    total_ta_da_cost = fields.Function(
        fields.Float('Total TA/DA Cost'),
        'get_total_ta_da')

    def get_total_renumeration(self, name):
        '''Calculate total Renumeration amount of Exam'''
        res = 0
        if self.employees:
            for employee in self.employees:
                if employee.renumeration_bill:
                    res += employee.renumeration_bill.net_amount
        return res

    def get_total_ta_da(self, name):
        '''Calculate total TA/DA amount of Exam'''
        res = 0
        if self.employees:
            for employee in self.employees:
                if employee.ta_da_bill:
                    res += employee.ta_da_bill.total_amount
        return res

    @fields.depends('exam_type', 'date_from')
    def on_change_with_name(self):
        '''Change value of name field using exam_type and date_from field'''
        return '{} {}'.format(
            self.exam_type.name if self.exam_type else '',
            self.date_from.year if self.date_from else '',
        )
    
    @classmethod
    def __setup__(cls):
        '''Setup error messages, workflow transitions, and button properties
           when an instance of this class is initialized'''
        super().__setup__()
        cls._error_messages.update({
            'bill_not_submitted': 'Bill not submitted',
            'bill_not_approved': 'Bill not approved',
        })
        cls._transitions = set((
            ('draft', 'confirm'),
            ('confirm', 'approved'),
            ('approved', 'in_progress'),
            ('in_progress', 'awaiting_ta_da'),
            ('awaiting_ta_da', 'ta_da_submit'),
            ('ta_da_submit', 'aao_approval'),
            ('aao_approval', 'ao_approval'),
            ('ao_approval', 'ace_approval'),
            ('ace_approval', 'adean_approval'),
            ('adean_approval', 'dean_approval'),
            ('dean_approval', 'ao_approval_2'),
            ('ao_approval_2', 'approval'),
            ('approval', 'budget_allocation'),
            ('budget_allocation', 'final_process')
        ))
        cls._buttons.update({
            'confirm_data': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'approve': {
                'invisible': ~Eval('state').in_(['confirm'])
            },
            'send_in_progress': {
                'invisible': ~Eval('state').in_(['approved'])
            },
            'generate_ta_da_bills': {
                'invisible': ~Eval('state').in_(['in_progress'])
            },
            'submit_ta_da_bills': {
                'invisible': ~Eval('state').in_(['awaiting_ta_da'])
            },
            'send_for_aao_approval': {
                'invisible': ~Eval('state').in_(['ta_da_submit'])
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
            'approve_ta_da': {
                'invisible': ~Eval('state').in_(['ao_approval_2'])
            },
            'send_for_budget_allocation': {
                'invisible': ~Eval('state').in_(['approval'])
            },
            'send_for_final_process': {
                'invisible': ~Eval('state').in_(['budget_allocation'])
            }
        })

    @classmethod
    def view_attributes(cls):
        '''States given for Renumeration and TA/DA bills
        notebook pages in form view'''
        return [
            ('/form/notebook/page[@id="_renumeration"]',
                'states', cls._RENUM_PAGE_STATES),
            ('/form/notebook/page[@id="_ta_da"]',
                'states', cls._TA_DA_PAGE_STATES),
        ]

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def get_current_exam():
        '''Function to fetch the current exam'''
        exam_record = list(Transaction().timestamp.keys())[0]
        exam_table_and_id = exam_record.split(',')
        exam_table = exam_table_and_id[0]
        exam_id = exam_table_and_id[1]
        pool = Pool()
        Exam = pool.get(exam_table)
        current_exam = Exam.search([('id', '=', exam_id)])[0]
        return current_exam

    @classmethod
    def change_state_of_bills(cls, records, old_state, new_state):
        '''Change the state of all bills from old state to new state'''
        for record in records:
            bills_bundle = zip(
                record.renumeration_bills, record.ta_da_bills
            )
            for (renumeration_bill, ta_da_bill) in bills_bundle:
                if renumeration_bill.state in [old_state]:
                    renumeration_bill.state = new_state
                    renumeration_bill.save()
                if ta_da_bill.state in [old_state]:
                    ta_da_bill.state = new_state
                    if new_state in ['approved']:
                        ta_da_bill.approved_date = date.today()
                    ta_da_bill.save()
                else:
                    cls.raise_user_error('bill_not_submitted')

    @classmethod
    @Workflow.transition('confirm')
    def confirm_data(cls, records):
        '''Change status of exam to confirm'''
        pass

    @classmethod
    @Workflow.transition('approved')
    def approve(cls, records):
        '''Approve exam details and generate Renumeration Bills
           for employees involved in current exam'''
        current_exam = cls.get_current_exam()
        Renum = Pool().get('exam_section.renumeration_bill')
        for current_employee in current_exam.employees:
            renum_bill_for_employee = Renum.create([{
                'type_of_examiner': 'internal',
                'exam': current_exam,
                'employee': current_employee.employee,
                'designation': current_employee.employee.designation.name,
            }])[0]
            current_employee.renumeration_bill = renum_bill_for_employee
            current_employee.renumeration_bill.save()
            current_employee.save()

    @classmethod
    @Workflow.transition('in_progress')
    def send_in_progress(cls, records):
        '''Change status of exam to in_progress'''
        pass

    @classmethod
    @Workflow.transition('awaiting_ta_da')
    def generate_ta_da_bills(cls, records):
        '''
        Generate TA/DA and Contingency Bills for employees
        involved in current exam
        '''
        TADA = Pool().get('exam_section.ta_da_bill')
        Contingency = Pool().get('exam_section.contingency_bill')
        current_exam = cls.get_current_exam()
        current_date_from = current_exam.date_from
        current_date_to = current_exam.date_to
        for current_employee in current_exam.employees:
            ta_da_bill_for_employee = TADA.create([{
                'employee': current_employee.employee,
                'designation':
                    current_employee.employee.designation,
                'department':
                    current_employee.employee.department,
                'exam': current_exam,
                'center': current_employee.center,
                'purpose':
                    'On deputation for {} examination from {} to {}'.format(
                        current_exam.name,
                        current_date_from.strftime("%d %B %Y"),
                        current_date_to.strftime("%d %B %Y")
                    )
            }])[0]
            current_employee.ta_da_bill = ta_da_bill_for_employee
            current_employee.ta_da_bill.save()
            contingency_bill_for_employee = Contingency.create([{
                'employee': current_employee.employee,
                'exam': current_exam,
                'exam_center': current_employee.center,
            }])[0]
            current_employee.contingency_bill = contingency_bill_for_employee
            current_employee.contingency_bill.save()
            current_employee.save()

    @classmethod
    @Workflow.transition('ta_da_submit')
    def submit_ta_da_bills(cls, records):
        for record in records:
            all_bills = zip(
                record.renumeration_bills,
                record.ta_da_bills
            )
            for (bill1, bill2) in all_bills:
                if bill1.state in ['draft'] or \
                        bill2.state in ['draft']:
                    cls.raise_user_error('bill_not_submitted')
        pass

    '''Button functions for executing workflow transitions'''
    @classmethod
    @Workflow.transition('aao_approval')
    def send_for_aao_approval(cls, records):
        '''Change status of exam and bills to aao_approval'''
        cls.change_state_of_bills(records, 'confirm', 'aao_approval')

    @classmethod
    @Workflow.transition('ao_approval')
    def send_for_ao_approval(cls, records):
        '''Change status of exam and bills to ao_approval'''
        cls.change_state_of_bills(records, 'aao_approval', 'ao_approval')

    @classmethod
    @Workflow.transition('ace_approval')
    def send_for_ace_approval(cls, records):
        '''Change status of exam and bills to ace_approval'''
        cls.change_state_of_bills(records, 'ao_approval', 'ace_approval')

    @classmethod
    @Workflow.transition('adean_approval')
    def send_for_adean_approval(cls, records):
        '''Change status of exam and bills to adean_approval'''
        cls.change_state_of_bills(records, 'ace_approval', 'adean_approval')

    @classmethod
    @Workflow.transition('dean_approval')
    def send_for_dean_approval(cls, records):
        '''Change status of exam and bills to dean_approval'''
        cls.change_state_of_bills(records, 'adean_approval', 'dean_approval')

    @classmethod
    @Workflow.transition('ao_approval_2')
    def send_for_ao_approval_2(cls, records):
        '''Change status of exam and bills to ao_approval_2'''
        cls.change_state_of_bills(records, 'dean_approval', 'ao_approval_2')

    @classmethod
    @Workflow.transition('approval')
    def approve_ta_da(cls, records):
        '''Change status of exam to approval and status bills to approved'''
        cls.change_state_of_bills(records, 'ao_approval_2', 'approved')

    @classmethod
    @Workflow.transition('budget_allocation')
    def send_for_budget_allocation(cls, records):
        '''Change status of exam to budget_allocation'''
        pass

    @classmethod
    @Workflow.transition('final_process')
    def send_for_final_process(cls, records):
        '''Change status of exam to final_process'''
        pass


class Centers(ModelSQL, ModelView):
    '''Exam Centers'''

    __name__ = 'exam.centers'

    location = fields.Many2One('exam_section.exam_center', 'Location')
    exam = fields.Many2One('exam_section.exam', 'Exam')
    employees = fields.One2Many('exam.employees', 'center', 'Employees')
    location_code = fields.Char('Code')
    employee_count = fields.Function(
        fields.Integer('Count'),
        'on_change_with_employee_count')
    center_hidden = fields.Many2One(
        'exam.employees',
        'Employee-Center'
    )
    name = fields.Char('Name')

    @fields.depends('location', 'location_code')
    def on_change_with_location_code(self):
        '''Get current center code'''
        if self.location:
            return self.location.code if self.location.code else ''

    @fields.depends('location')
    def on_change_with_name(self):
        '''Get current center name'''
        if self.location:
            return self.location.name if self.location.name else ''

    @fields.depends('employees')
    def on_change_with_employee_count(self, name=None):
        '''Calculate number of employees involved in current exam'''
        return len(self.employees)


class Employees(ModelSQL, ModelView):
    '''Employees'''

    __name__ = 'exam.employees'

    employee = fields.Many2One('company.employee', 'Employee')
    group = fields.Char('Group')
    grade = fields.Many2One('company.employee.grade', 'Pay Matrix Level')
    center = fields.Many2One(
        'exam.centers',
        'City',
        domain=[('id', 'in', Eval('centers'))],
        depends=['centers']
    )
    address = fields.Many2One(
        'exam_section.exam_center.address',
        'Center',
        domain=[('center', '=', Eval('location'))],
        depends=['centers']
    )
    location = fields.Function(
        fields.Many2One('exam_section.exam_center', 'Location'),
        'on_change_with_location',
    )
    centers = fields.Function(
        fields.One2Many(
            'exam.centers',
            'center_hidden',
            'List of centers'
        ),
        'on_change_with_centers'
    )
    exam = fields.Many2One('exam_section.exam', 'Exam')
    renumeration_bill = fields.Many2One(
        'exam_section.renumeration_bill',
        'Renumeration Bill'
    )
    ta_da_bill = fields.Many2One('exam_section.ta_da_bill', 'TA/DA Bill')
    contingency_bill = fields.Many2One(
        'exam_section.contingency_bill', 'Contingency Bill'
    )
    date_payable = fields.Date('Date')

    @classmethod
    def __setup__(cls):
        super(Employees, cls).__setup__()
        t = cls.__table__()
        cls._sql_constraints = [
            ('employee_exam_unique', Unique(t, t.employee, t.exam),
                'Same Employee cannot be added again in the same exam'
            ),
        ]
    
    @fields.depends('exam')
    def on_change_with_centers(self, name=None):
        '''Get centers selected for current exam'''
        if self.exam and self.exam.centers:
            return [center.id for center in self.exam.centers]

    @fields.depends('employee')
    def on_change_with_group(self):
        '''Get group of employee'''
        if self.employee and self.employee.employee_group:
            return self.employee.employee_group
    
    @fields.depends('employee')
    def on_change_with_grade(self):
        '''Get pay matrix level of employee'''
        if self.employee and self.employee.grade:
            return self.employee.grade.id
    
    @fields.depends('center')
    def on_change_with_location(self, name=None):
        '''Get current location for current exam'''
        if self.center:
            return self.center.location.id
    