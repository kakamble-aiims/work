from trytond.model import ModelView, ModelSQL, fields, Workflow
from trytond.wizard import Wizard, StateView, StateTransition, \
    StateAction, Button
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'ExamCenter', 
    'Exam',
    'Centers', 'Employees', 'GetTADABill', 'GetTADABillView',
    'GetRenumerationBill', 'GetRenumerationBillView'
    ]

class ExamCenter(ModelSQL, ModelView):
    '''Exam Center'''

    __name__ = 'exam_section.exam_center'

    state = fields.Many2One(
        'country.subdivision',
        'State',
        domain=[('country.name', '=', 'India')]
        )
    city = fields.Char('City')
    code = fields.Char('Code', required="True")
    address = fields.Char('Address')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.__repr__ = 'code'


class Exam(Workflow, ModelSQL, ModelView):
    '''Exam'''

    __name__ = 'exam_section.exam'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('approved', 'Approved'),
        ('in_progress', 'In Progress'),
        ('awaiting_ta_da', 'Awaiiting TA/DA Bills'),
        ('ta_da_submit', 'TA/DA Submit'),
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
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('state').in_([
                'draft',
                'confirm',
                'approved',
                'in_progress'
            ]),
        },
        depends=['state']
    )
    ta_da_bills = fields.One2Many(
        'exam_section.ta_da_bill',
        'exam',
        'TA/DA Bills',
        states={
            'readonly': ~Eval('state').in_(['draft']),
            'invisible': ~Eval('state').in_([
                'draft',
                'confirm',
                'approved',
                'in_progress'
            ]),
        },
        depends=['state']
    )
    total_renumeration_cost = fields.Function(
        fields.Float('Total Renumeration Cost'),
        'get_total_renumeration')
    total_ta_da_cost = fields.Function(
        fields.Float('Total TA/DA Cost'),
        'get_total_ta_da')

    def get_total_renumeration(self, name):
        res = 0
        if self.employees:
            for employee in self.employees:
                if employee.renumeration_bill:
                    res += employee.renumeration_bill.net_amount
        return res

    def get_total_ta_da(self, name):
        res = 0
        if self.employees:
            for employee in self.employees:
                if employee.ta_da_bill:
                    res += employee.ta_da_bill.total_amount
        return res

    @fields.depends('exam_type', 'date_from')
    def on_change_with_name(self):
            return '{} {}'.format(
                self.exam_type.name if self.exam_type else '',
                self.date_from.year if self.date_from else '',
            )
    
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions = set((
            ('draft', 'confirm'),
            ('confirm', 'approved'),
            ('approved', 'in_progress'),
            ('in_progress', 'awaiting_ta_da'),
            ('awaiting_ta_da', 'ta_da_submit'),
            ('ta_da_submit', 'approval'),
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
            'approve_ta_da': {
                'invisible': ~Eval('state').in_(['ta_da_submit'])
            },
            'send_for_budget_allocation': {
                'invisible': ~Eval('state').in_(['approval'])
            },
            'send_for_final_process': {
                'invisible': ~Eval('state').in_(['budget_allocation'])
            }
        })

    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def get_current_exam():
        exam_record = list(Transaction().timestamp.keys())[0]
        exam_table_and_id = exam_record.split(',')
        exam_table = exam_table_and_id[0]
        exam_id = exam_table_and_id[1]
        pool = Pool()
        Exam = pool.get(exam_table)
        current_exam = Exam.search([('id', '=', exam_id)])[0]
        return current_exam

    @classmethod
    @Workflow.transition('confirm')
    def confirm_data(cls, records):
        pass

    @classmethod
    @Workflow.transition('approved')
    def approve(cls, records):
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
        pass

    @classmethod
    @Workflow.transition('awaiting_ta_da')
    def generate_ta_da_bills(cls, records):
        TADA = Pool().get('exam_section.ta_da_bill')
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
                'purpose':
                    'On deputation for {} examination from {} to {}'.format(
                        current_exam.name,
                        current_date_from.strftime("%d %B %Y"),
                        current_date_to.strftime("%d %B %Y")
                    )
            }])[0]
            current_employee.ta_da_bill = ta_da_bill_for_employee
            current_employee.ta_da_bill.save()
            current_employee.save()

    @classmethod
    @Workflow.transition('ta_da_submit')
    def submit_ta_da_bills(cls, records):
        pass

    @classmethod
    @Workflow.transition('approval')
    def approve_ta_da(cls, records):
        pass

    @classmethod
    @Workflow.transition('budget_allocation')
    def send_for_budget_allocation(cls, records):
        pass

    @classmethod
    @Workflow.transition('final_process')
    def send_for_final_process(cls, records):
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
        'get_total_employees')
    # TODO: Change the method to on_change_with
    
    @fields.depends('location', 'location_code')
    def on_change_with_location(self):
        self.location_code = self.location.code
     
    def get_total_employees(self, name):
        res = 0
        for x in self.employees:
            print(x.employee)
            res += 1
        return res


class Employees(ModelSQL, ModelView):
    '''Employees'''

    __name__ = 'exam.employees'
    _rec_name = "employee"

    employee = fields.Many2One('company.employee', 'Employee')
    center = fields.Many2One(
        'exam.centers',
        'Center',
        domain=[('id', 'in', Eval('centers'))]
    )
    centers_list = fields.Function(
        fields.Char('List of centers'),
        'on_change_with_centers_list'
    )
    exam = fields.Many2One('exam_section.exam', 'Exam')
    renumeration_bill = fields.Many2One(
        'exam_section.renumeration_bill',
        'Renumeration Bill'
        )
    ta_da_bill = fields.Many2One('exam_section.ta_da_bill', 'TA/DA Bill')
    date_payable = fields.Date('Date')

    @fields.depends('exam')
    def on_change_with_centers_list(self, name=None):
        if self.exam:
            centers = self.get_centers_of_exam() if self.exam.centers else ''
            return centers
    
    def get_centers_of_exam(self):
        centers = [center.id for center in self.exam.centers]
        return str(centers)
        
       
    @classmethod
    @ModelView.button
    @ModelView.button_action('exam_section.act_wizard_get_ta_da_bill')
    def get_ta_da_bill(cls, records):
        pass


class GetTADABillView(ModelView):
    '''Get TA/DA Bill view'''

    __name__ = 'exam.get_ta_da_bill.view'

    employee = fields.Many2One('company.employee', 'Employee', readonly=True)
    exam = fields.Many2One('exam_section.exam', 'Exam')
    ta_da_bill = fields.Many2One('exam_section.ta_da_bill', 'TA/DA Bill')

    @staticmethod
    def default_employee():
        current_employee = Transaction().context.get('employee')
        return current_employee


class GetTADABill(Wizard):
    '''Get TA/DA Bill for employee'''
    
    __name__ = 'exam.get_ta_da_bill'

    start_state = 'details'
    details = StateView(
        'exam.get_ta_da_bill.view',
        'exam_section.form_get_ta_da_bill',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'save_details', 'tryton-go-next', default=True)
        ]
    )
    save_details = StateTransition()
    fill = StateAction('exam_section.act_ta_da_bill')

    def transition_save_details(self):
        Employee = Pool().get('exam.employees')
        current_employee = Employee.search([
                ('employee', '=', self.details.employee),
                ('exam', '=', self.details.exam)
            ])[0]
        self.details.ta_da_bill = current_employee.ta_da_bill    
        return 'fill'        
    
    def do_fill(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
            ('id', '=', self.details.ta_da_bill.id)
        ])
        return action, {}


class GetRenumerationBillView(ModelView):
    '''Get TA/DA Bill view'''

    __name__ = 'exam.get_renumeration_bill.view'

    employee = fields.Many2One('company.employee', 'Employee')
    exam = fields.Many2One('exam_section.exam', 'Exam')
    renumeration_bill = fields.Many2One(
        'exam_section.renumeration_bill',
        'Renumeration Bill'
    )

    @staticmethod
    def default_employee():
        current_employee = Transaction().context.get('employee')
        return current_employee


class GetRenumerationBill(Wizard):
    '''Get TA/DA Bill for employee'''
    
    __name__ = 'exam.get_renumeration_bill'

    start_state = 'details'
    details = StateView(
        'exam.get_renumeration_bill.view',
        'exam_section.form_get_renumeration_bill',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'save_details', 'tryton-go-next', default=True)
        ]
    )
    save_details = StateTransition()
    fill = StateAction('exam_section.act_renumeration_bill')

    def transition_save_details(self):
        Employee = Pool().get('exam.employees')
        current_employee = Employee.search([
                ('employee', '=', self.details.employee),
                ('exam', '=', self.details.exam)
            ])[0]
        self.details.renumeration_bill = \
            current_employee.renumeration_bill    
        return 'fill'        
    
    def do_fill(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
            ('id', '=', self.details.renumeration_bill.id)
        ])
        return action, {}