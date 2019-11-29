import requests
import random
import pdb
import hashlib
from hashlib import *
from datetime import datetime, timedelta
from trytond.model import (ModelSQL, ModelView, Workflow, fields)
from trytond.pyson import Eval, Bool, PYSONEncoder, If, Or, Not, And
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta


__all__ = [
    'Department',
    'AparDepartmentForm', 'EmployeeForms',
    'AparEmployeeFormSectionLine', 'AparEmployeeFormSection',
    'EmployeeFormLine', 'EmployeeFormSignature',
    'EmployeeFormPart', 'APARGenerateFormsShow',
    'APARGenerateForms',
]


class Department(metaclass=PoolMeta):
    """Departments"""

    __name__ = "company.department"

    is_apar_generated = fields.Boolean('Is APAR Generated for Current Year?')

    @staticmethod
    def default_is_apar_generated():
        return False


class AparDepartmentForm(ModelSQL, ModelView):
    'Apar Department'

    __name__ = 'apar.department.form'

    department = fields.Many2One('company.department', 'Department')
    establishment = fields.Many2One(
        'health.establishment', 'Establishment')
    head = fields.Many2One('company.employee', 'Head of Department')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    date_forward_to_employee = fields.Date(
        'Forwarded to Employees on', readonly=True)
    forward_to_employee_by = fields.Many2One(
        'res.user', 'Forwarded to Employees by', readonly=True)

    employee_forms = fields.One2Many(
        'apar.employee.form', 'department_form', 'APAR Employee Form')

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed')
        ], 'Status', readonly=True
    )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "forward_to_employees": {
                'invisible': Eval('state') != 'draft',
                'depends': ['state']
            }
        })

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @ModelView.button
    def forward_to_employees(cls, records):
        EmployeeForm = Pool().get('apar.employee.form')
        for record in records:
             # Change the state of all the employee forms
            EmployeeForm.forward_to_employee(record.employee_forms)
            record.forward_to_employee_by = Transaction().user
            Date = Pool().get('ir.date')
            record.date_forward_to_employee = Date.today()
            record.state = 'in_progress'
            record.save()


class EmployeeForms(Workflow, ModelSQL, ModelView):
    'Employee Forms'

    __name__ = 'apar.employee.form'

    form_name = fields.Char("Form Name", readonly=True)
    employee_code = fields.Char('Employee Code', readonly=True)
    employee = fields.Many2One(
        'company.employee', 'Employee', required=True, readonly=True)
    reporting_officer = fields.Many2One(
        'company.employee', 'Reporting Officer', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'], )
    reporting_officer_period = fields.Char(
        'Period covered under Reporting Officer', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    reviewing_officer = fields.Many2One(
        'company.employee', 'Reviewing Officer', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    reviewing_officer_period = fields.Char(
        'Period covered under Reviewing Officer', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    acceptance_authority = fields.Many2One(
        'company.employee', 'Acceptance Authority', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    accepting_authority_period = fields.Char(
        'Period covered under Accepting Authority', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    department_form = fields.Many2One(
        'apar.department.form', 'Department Forms')
    department = fields.Many2One(
        'company.department', 'Department / Section / Unit', readonly=True)
    date_from = fields.Date('Date From', readonly=True)
    date_to = fields.Date('Date To', readonly=True)
    designation = fields.Many2One(
        'employee.designation', 'Designation', readonly=True)
    date_of_joining = fields.Date(
        'Date of Joining the Service', readonly=True)
    date_of_birth = fields.Date('Date of Birth', readonly=True)
    category = fields.Selection(
        [
            (None, ''),
            ('general', 'General'),
            ('sc', 'Scheduled Caste'),
            ('st', 'Scheduled Tribe'),
            ('obc', 'Other Backward Classes'),
            ('ph', 'Physically Handicapped')
        ], 'Category', readonly=True
    )
    date_appointment = fields.Date(
        'Appointment', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    present_grade = fields.Many2One(
        'company.employee.grade', 'Pay Matrix Level', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    present_post = fields.Many2One(
        'employee.designation', 'Present Post', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    date_posting_present_post = fields.Date(
        'Date of Posting on Present Post', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    discontinuity_period_leave = fields.Text(
        'Period of Discontinuity (Leave)', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    discontinuity_period_official = fields.Text(
        'Period of Discontinuity (Official)', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    qualification = fields.Text(
        'Academic and Professional Qualifications', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    courses_undertaken = fields.Text(
        'Training and Courses Undertaken', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)

    professional_bodies = fields.Text(
        'Membership of Professional Bodies', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    pay_in_band = fields.Char(
        'Pay in the Pay Band', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    grade_pay = fields.Many2One(
        'company.employee.grade_pay', 'Grade Pay', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])

    parts = fields.One2Many(
        'apar.employee.form.part', 'employee_form', 'Parts',
    )
    part_self_appraisal = fields.One2Many(
        'apar.employee.form.part', 'employee_form_appraisal', 'Self Appraisal',
    )
    part_appraisal = fields.One2Many(
        'apar.employee.form.part', 'employee_form_reporting', 'Appraisal',
    )
    part_review = fields.One2Many(
        'apar.employee.form.part', 'employee_form_reviewing', 'Reiew',
    )
    part_accepting = fields.One2Many(
        'apar.employee.form.part', 'employee_form_accepting', 'Accepting',
    )
    signatures = fields.One2Many(
        'apar.employee.form.signature', 'employee_form', 'Signatures')
    template = fields.Many2One('apar.form.template', 'Template')
    allow_representation = fields.Function(
        fields.Boolean('Allow Representation?'),
        'get_allow_representation',
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('no_initiation', 'No Inititation Certificate'),
            ('self_appraisal', 'Self Appraisal'),
            ('reporting_officer', 'Reporting Officer'),
            ('reviewing_officer', 'Reviewing Officer'),
            ('accepting_authority', 'Accepting Authority'),
            ('disclose', 'Disclose'),
            ('signed', 'Signed by Ratee Officer'),
            ('representation', 'Raised Representation')
        ], 'Status', required=True, readonly=True
    )
    representation = fields.Many2One('apar.representation','Representation')
    grade = fields.Float(
        'Grade', readonly=True, states={
            'invisible': ~Eval('state').in_(
                [
                    'reviewing_officer', 
                    'accepting_authority', 
                    'disclose', 
                    'signed', 
                    'representation'
                ]),
        }, depends=['state'],)
    grade_label = fields.Selection(
        [
            (None, ''),
            ('9', '9 - Outstanding'),
            ('7', '7 - Very Good'),
            ('5', '5 - Good'),
            ('3', '3 - Satisfactory'),
            ('0', '0 - Unsatisfactory'),
        ], 'Grades', readonly=True, states={
            'invisible': ~Eval('state').in_(
                [
                    'reviewing_officer',
                    'accepting_authority', 
                    'disclose', 
                    'signed', 
                    'representation'
                ]),
        }, depends=['state'],
        
        )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'officer_missing': (
                'Please fill Reporting Officer and Reviewing Officer.'),
            'missing_sign': (
                'Please sign the document before forwarding.'),
            'blank_grades': (
                'It seems that you have not filled any grade for some questions. ' \
                'Please fill in all the grades before forwarding.')
        })
        cls._buttons.update({
            "forward_to_employee": {
                'invisible': ~Eval('state').in_(['draft']),
                'depends': ['state']                   
            },
            "submit_to_reporting": {
                'invisible': ~Eval('state').in_(['self_appraisal']),
                'depends': ['state']
            },
            "submit_to_reviewing": {
                'invisible': ~Eval('state').in_(['reporting_officer']),
                'depends': ['state']
            },
            "submit_to_accepting": {
                'invisible': ~Eval('state').in_(['reviewing_officer']) | ~Eval('acceptance_authority'),
                'depends': ['state']
            },
            "disclose": {
                'invisible': If(
                    Bool(Eval('acceptance_authority')),
                    ~Eval('state').in_(['accepting_authority']),
                    ~Eval('state').in_(['reviewing_officer']),
                ),
                'depends': ['state']
            },
            "sign_and_submit": {
                'invisible': ~Eval('state').in_(['disclose']),
                'depends': ['state']
            },
            "raise_representation": {
                'invisible': Or(~Eval('state').in_(
                    ['disclose', 'signed']), Bool(~Eval('allow_representation'))),
                'depends': ['state', 'allow_representation']
            }
        })

        cls._transitions |= set((
            ('draft', 'self_appraisal'),
            ('draft', 'no_initiation'),
            ('self_appraisal', 'reporting_officer'),
            ('reporting_officer', 'reviewing_officer'),
            ('reviewing_officer', 'accepting_authority'),
            ('reviewing_officer', 'disclose'),
            ('accepting_authority', 'disclose'),
            ('disclose', 'signed'),
            ('disclose', 'representation'),
            ('signed', 'representation')
        ))

    @staticmethod
    def default_state():
        return 'draft'
    
    def default_grade_label():
        return None

    def edit_questions(self, parts):
        """Make questions editable of relevant parts."""
        for part in parts:
            for question in part.questions:
                question.is_editable = True
                question.save()

    @classmethod
    def get_allow_representation(cls, records, field):
        """Check if the representation can be allowed"""
        vals = {}
        for record in records:
            vals[record.id] = False
            for sign in record.signatures:
                if sign.action == 'signed':
                    if sign.signed_on >= datetime.now() - timedelta(days=15):
                        vals[record.id] = True
        return vals

    def form_signature(self, action):

        pool = Pool()
        sign_obj = pool.get('apar.employee.form.signature')
        User = pool.get('res.user')
        user = User(Transaction().user)

        employee = user.employee
        place = 'Delhi'

        vals = {
            'signed_by_user': user.id,
            'signed_by_employee': employee.id if employee else None,
            'designation': employee.designation.id if employee else None,
            'signed_on': datetime.now(),
            'employee_form': self.id,
            'place': place,
            'action': self.state,
        }

        sign_obj.create([vals])

    @classmethod
    @Workflow.transition('no_initiation')
    def no_initiation(cls, records):
        for record in records:
            Pool().get('apar.employee.form.part').delete(record.parts)

    @classmethod
    @ModelView.button
    @Workflow.transition('self_appraisal')
    def forward_to_employee(cls, records):
        pool = Pool()
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')
        reporting_group = ModelData.get_id('apar', 'group_reporting_officer')
        reviewing_group = ModelData.get_id('apar', 'group_reviewing_officer')
        accepting_group = ModelData.get_id('apar', 'group_accepting_authority')

        
        for record in records:
            if (record.date_to and 
                    (record.date_to - record.date_from).days < 90):
                cls.no_initiation([record])
                record.form_signature('forward_to_employee')
                continue

            if (not record.reporting_officer or not record.reviewing_officer):
                    cls.raise_user_error('officer_missing')
            record.form_signature('forward_to_employee')
            record.edit_questions(record.part_self_appraisal)

            # Give the user access to reporting and reviewing officer as
            # assigned by the Head of Department
            reporting_officer_users = User.search(
                [('employee', '=', record.reporting_officer)])
            for reporting_officer_user in reporting_officer_users:
                reporting_officer_user_groups = list(reporting_officer_user.groups)
                if reporting_group not in reporting_officer_user_groups:
                    reporting_officer_user_groups.append(reporting_group)
                    reporting_officer_user.groups = reporting_officer_user_groups
                    reporting_officer_user.save()

            reviewing_officer_users = User.search(
                [('employee', '=', record.reviewing_officer)])
            for reviewing_officer_user in reviewing_officer_users:
                reviewing_officer_user_groups = list(reviewing_officer_user.groups)
                if reviewing_group not in reviewing_officer_user_groups:
                    reviewing_officer_user_groups.append(reviewing_group)
                    reviewing_officer_user.groups = reviewing_officer_user_groups
                    reviewing_officer_user.save()

            if record.acceptance_authority:
                acceptance_officer_users = User.search(
                    [('employee', '=', record.acceptance_authority)])
                for acceptance_officer_user in acceptance_officer_users:
                    acceptance_officer_user_groups = list(acceptance_officer_user.groups)
                    if accepting_group not in acceptance_officer_user_groups:
                        acceptance_officer_user_groups.append(accepting_group)
                        acceptance_officer_user.groups = acceptance_officer_user_groups
                        acceptance_officer_user.save()

    @classmethod
    @ModelView.button
    @Workflow.transition('reporting_officer')
    def submit_to_reporting(cls, records):
        for record in records:
            record.form_signature('reporting_officer')
            record.edit_questions(record.part_appraisal)

            # Modify the states of Grade Questions for allowing Reporting
            # Officer to edit them.
            for part in record.parts:
                for section in part.sections:
                    for question in section.questions:
                        question.state = 'reporting_officer'
                        question.save()

    @classmethod
    @ModelView.button
    @Workflow.transition('reviewing_officer')
    def submit_to_reviewing(cls, records):
        for record in records:
            # Copy grades from reporting to reviewing
            for part in record.parts:
                for section in part.sections:
                    for question_line in section.questions:
                        if question_line.grade_reporting is None:
                            cls.raise_user_error("blank_grades")
                        question_line.grade_reviewing = question_line.grade_reporting
                        question_line.state = 'reviewing_officer'
                        question_line.save()
                part.is_sections = True

            record.form_signature('reviewing_officer')
            record.edit_questions(record.part_review)

    @classmethod
    @ModelView.button
    @Workflow.transition('accepting_authority')
    def submit_to_accepting(cls, records):
        for record in records:
            record.form_signature('accepting_authority')
            record.edit_questions(record.part_accepting)
            for part in record.parts:
                for section in part.sections:
                    for question in section.questions:
                        question.state = None
                        question.save()

    @classmethod
    @ModelView.button
    @Workflow.transition('disclose')
    def disclose(cls, records):
        for record in records:
            # Copy the grade from the part
            part = record.part_appraisal[0]
            grade_ = part.overall_score_reviewing
            record.grade = grade_

            if grade_ <= 10 and grade_ >= 8:
                record.grade_label = '9'
            elif grade_ <8 and grade_ >= 6:
                record.grade_label = '7'
            elif grade_ <6 and grade_ >= 4:
                record.grade_label = '5'
            else:
                record.grade_label = '0'
            record.save()
            record.form_signature('disclose')
            for part in record.parts:
                for section in part.sections:
                    for question in section.questions:
                        question.state = None
                        question.save()

    @classmethod
    @ModelView.button
    @Workflow.transition('signed')
    def sign_and_submit(cls, records):
        for record in records:
            record.date_signed_ratee = datetime.now().date
            record.form_signature('signed')
            record.save()

    @classmethod
    @ModelView.button
    @ModelView.button_action('apar.act_wizard_generate_res_wizard')
    def raise_representation(cls, records):
        '''Method to raise the wizard'''

    @classmethod
    @Workflow.transition('representation')
    def set_representation(cls, records):
        '''Method to call the workflow transition'''
        for record in records:
            record.form_signature('raise_representation')

    @classmethod
    def update_configuration(cls, field):
        Config = Pool().get('apar.form.template.configuration')
        config_rec = Config(1)
        date = getattr(config_rec, field)
        Config.write(config_rec, {field: date + timedelta(days=365)})

    # Cron methods
    @classmethod
    def cron_last_date_emp_fill(cls):
        """If the employee doesn't fill it, then move on next step"""
        # Check which forms are not filled yet. Not searching on current year as
        # it is understood that all other forms are closed automatically.
        # Move them to the next state
        records = cls.search([('state', '=', 'self_appraisal')])
        cls.submit_to_reporting(records)
        cls.update_configuration('last_date_emp_fill')

    @classmethod
    def cron_last_date_reporting(cls):
        """If the reporting doesn't fill the form, then move on next step"""
        records = cls.search([('state', '=', 'reporting_officer')])
        cls.submit_to_reviewing(records)
        cls.update_configuration('last_date_reporting')

    @classmethod
    def cron_last_date_reviewing(cls):
        """If the reviewing doesn't fill the form, then move on next step"""
        records = cls.search([('state', '=', 'reporting_officer')])
        cls.submit_to_reviewing(records)
        cls.update_configuration('last_date_reviewing')

    @classmethod
    def cron_last_date_accepting(cls):
        """If the accepting doesn't fill the form, then move on next step"""
        records = cls.search([('state', '=', 'reporting_officer')])
        cls.submit_to_reviewing(records)
        cls.update_configuration('last_date_accepting')

    @classmethod
    def cron_last_date_emp_sign(cls):
        """If the employee doesn't sign the form, then move on next step"""
        records = cls.search([('state', '=', 'reporting_officer')])
        cls.submit_to_reviewing(records)
        cls.update_configuration('last_date_emp_sign')


    @classmethod
    def view_attributes(cls):
        pyson1 = And(
            Eval('employee') == Eval('context', {}).get('employee', ''),
            ~Eval('state').in_(['disclose', 'signed', 'representation'])
        )
        attribute = [
            ("//page[@id='appraisal']", "states", {"invisible": pyson1}),
            ("//page[@id='reviewing']", "states", {"invisible": pyson1}),
            ("//page[@id='accepting']", "states", {"invisible": pyson1}),
        ]
        return attribute


class EmployeeFormPart(Workflow, ModelSQL, ModelView):
    "Employee Form Part"

    __name__ = "apar.employee.form.part"

    number = fields.Char('Part Number', required=True)
    name = fields.Char('Part Name', required=True)
    is_sections = fields.Boolean('Have Sections?')
    questions = fields.One2Many('apar.employee.form.line', 'part', 'Questions')
    sections = fields.One2Many(
        'apar.employee.form.section', 'part', 'Sections', states={
            'invisible': ~Bool(Eval('is_sections'))
        }, depends=['is_sections'],)
    overall_score_reporting = fields.Function(fields.Float(
        'Overall Grade - Reporting',
        states={
            'invisible': ~Bool(Eval('is_sections')),
        }, depends=['is_sections']), 'get_reporting_grades')
    overall_score_reviewing = fields.Function(fields.Float(
        'Overall Grade - Reviewing',
        states={
            'invisible': ~Bool(Eval('is_sections')),
        }, depends=['is_sections']), 'get_reviewing_grades')
    # signatures = fields.One2Many(
    #     'apar.employee.form.part.signature', 'part', 'Signatures')
    employee_form = fields.Many2One('apar.employee.form', 'Employee Form', ondelete='CASCADE')
    employee_form_appraisal = fields.Many2One(
        'apar.employee.form', 'Employee Form Self Appraisal', ondelete='CASCADE')
    employee_form_reporting = fields.Many2One(
        'apar.employee.form', 'Employee Form Reporting', ondelete='CASCADE')
    employee_form_reviewing = fields.Many2One(
        'apar.employee.form', 'Employee Form Reviewing', ondelete='CASCADE')
    employee_form_accepting = fields.Many2One(
        'apar.employee.form', 'Employee Form Accepting', ondelete='CASCADE')
    otp = fields.Char('OTP', size=6, 
        states={
            'invisible': ~Eval('state').in_(['waiting_for_otp']),
        }, depends=['state'],)
    type_ = fields.Selection(
        [
            ('self_appraisal', 'Self Appraisal'),
            ('appraisal', 'Appraisal'),
            ('reviewing', 'Reviewing'),
            ('accepting','Accepting')
        ], 'Type'
    )
    otp_generate = fields.Char('OTP Generated')
    otp_generate_time = fields.DateTime('OTP Generated Time')
    state = fields.Selection(
        [
            ('unsigned', 'Unsigned'),
            ('waiting_for_otp', 'Waiting for Otp'),
            ('signed', 'Signed')
        ], 'State', readonly=True
    )

    signed_by_user = fields.Many2One(
        'res.user', 'Signed By', readonly=True,
        help="This will be filled by system.")
    signed_on = fields.DateTime('Signed On', readonly=True)
    note = fields.Text('Remarks')
    designation = fields.Many2One(
        'employee.designation', 'Designation', readonly=True)
    place = fields.Char('Place', readonly=True)


    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'invalid_otp': ("OTP Entered by you is invalid."),
            'missing_notes': ('''As per DOPT guidelines, if the grades are
                less than 4 or more than 8, then the remarks are mandatory.
                Please provide the remarks and then sign the part again.
            '''),
            'missing_contact': ("""Your mobile number is not updated in our records.
            Please contact your respective Establishment to get it updated
            in our records."""),
            'otp_expired': ("""Your OTP has expired, please generate new OTP by clicking
            Resend OTP button""")
        })

        c1 = Not(And(
            Eval('employee_form.state') == 'self_appraisal',
            Eval('employee') == Eval('context', {}).get('employee', '')
        ))
        c2 = Not(And(
            Eval('employee_form.state') == 'reporting_officer',
            Eval('reporting_officer') == Eval('context', {}).get('employee', '')
        ))
        c3 = Not(And(
            Eval('employee_form.state') == 'reviewing_officer',
            Eval('reviewing_officer') == Eval('context', {}).get('employee', '')
        ))
        c4 = Not(And(
            Eval('employee_form.state') == 'accepting_authority',
            Eval('acceptance_authority') == Eval('context', {}).get('employee', '')
        ))
        sign_this_doc_button = Or(
            Eval('state').in_(['waiting_for_otp', 'signed']),
            [c1, [c2, [c3, c4]]]
        )

        cls._buttons.update({
            "sign_this_document": {
                'invisible': sign_this_doc_button,
                'depends': ['state']
            },
            "form_signature_validate_otp":{
                'invisible': Eval('state').in_(
                    ['unsigned', 'signed']),
                'depends': ['state']
            },
            "resend_otp":{
                'invisible': Eval('state').in_(
                    ['unsigned', 'signed']),
                'depends': ['state']
            },
            "cancel_sign":{
                'invisible': Eval('state').in_(
                    ['unsigned', 'signed']),
                'depends': ['state']
            },
        })

        cls._transitions |= set((
            ('unsigned', 'waiting_for_otp'),
            ('waiting_for_otp', 'signed'),
            ('waiting_for_otp', 'unsigned')
        ))

    @staticmethod
    def default_state():
        return 'unsigned'
    
    @classmethod
    def create(cls, values):
        '''Overwrite the method to manage the parts.'''
        for vals in values:
            emp_form = vals.get('employee_form')
            if emp_form:
                type_ = vals.get('type_')
                if type_ == 'self_appraisal':
                    vals['employee_form_appraisal'] = emp_form
                elif type_ == 'appraisal':
                    vals['employee_form_reporting'] = emp_form
                elif type_ == 'reviewing':
                    vals['employee_form_reviewing'] = emp_form
                elif type_ == 'accepting':
                    vals['employee_form_accepting'] = emp_form
        return super().create(values)


    def notify_otp_to_user(self, otp_gen):
        message = """Dear Officer, OTP to digitally sign
            the APAR form is {otp}""".format(otp=otp_gen)
        # TODO: Get the value of logged in user's employee.
        contact = self.employee_form.employee.party.contact_mechanism_get('mobile')
        if not contact:
            self.raise_user_error("missing_contact")
        number = contact.value
        number = "9811292339"
        params = {
            'msg': message + " (%s)" % contact.value,
            'mobile': number,
        }
        url = "http://192.168.185.17/trytonsms/sendsms.aspx"
        requests.get(url, params)
        return True
        


    def generate_otp(self):
        # Generate OTP for the user
        self.otp_generate = ''.join(["%s" % random.randint(0, 9) for num in range(0, 6)])
        otp_gen = self.otp_generate
        self.otp_generate = hashlib.sha512(otp_gen.encode('utf-8')).hexdigest()
        self.otp_generate_time = datetime.now()
        self.save()
        self.notify_otp_to_user(otp_gen)

    def validate_otp(self):
        # Validate OTP
        s = hashlib.sha512(self.otp.encode('utf-8'))
        self.otp = s.hexdigest()
        if self.otp != self.otp_generate:
            self.raise_user_error('invalid_otp')
        if datetime.now() - self.otp_generate_time > timedelta(0, 0, 0, 0, 0, 6, 0):
            self.otp_generate = None
            self.raise_user_error('otp_expired')
        return True

    def _form_signature_validate_otp(self):
        self.validate_otp()
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        self.signed_by_user = user.id
        self.signed_by_employee = employee.id if employee else None
        self.designation = employee.designation.id if employee else None
        self.signed_on = datetime.now()
        self.place = 'Delhi'
        self._submit_employee_form()
        self.save()
 
    def _submit_employee_form(self):
        """Check and submit the employee form in next state"""

        # Make the questions non editable for the current part.
        for question in self.questions:
            question.is_editable = False
            question.save()

        # Move the form in next state
        type_ = self.type_
        if type_ == 'self_appraisal':
            self.employee_form_appraisal.submit_to_reporting([self.employee_form_appraisal])
        elif type_ == 'appraisal':
            self.employee_form_reporting.submit_to_reviewing([self.employee_form_reporting])
        elif type_ == 'reviewing':
            if self.employee_form_reviewing.acceptance_authority:
                self.employee_form_reviewing.submit_to_accepting([self.employee_form_reviewing])
            else:
                self.employee_form_reviewing.disclose([self.employee_form_reviewing])
        elif type_ == 'accepting':
            self.employee_form_accepting.disclose([self.employee_form_accepting])

    def check_grades_remarks(self):
        '''As per DOPT guidelines: If the grades given by the Reviewing officer are
        less than 4 or more than 8, then we need to check if the proper remarks
        have been given or not.'''
        if not self.employee_form.state == 'reviewing_officer':
            return True
        if self.employee_form.grade_label in ('9', '0') and not self.note:
            self.raise_user_error('missing_notes')
        return True

    @classmethod
    @ModelView.button
    def resend_otp(cls, records):
        for record in records:
            record.generate_otp()

    @classmethod
    @ModelView.button
    @Workflow.transition('unsigned')
    def cancel_sign(cls, records):
        for record in records:
            record.generate_otp = None

    @classmethod
    @ModelView.button
    @Workflow.transition('waiting_for_otp')
    def sign_this_document(cls, records):
        for record in records:
            record.generate_otp()

    @classmethod
    @ModelView.button
    @Workflow.transition('signed')
    def form_signature_validate_otp(cls, records):
        for record in records:
            #TODO: Check if the OTP Generated Time is less than 6 hours. Else raise the
            # message that it is expired. Please generate new OTP by clicking Resend OTP
            # button.
            record._form_signature_validate_otp()

    @classmethod
    @Workflow.transition('unsigned')
    def form_unsign(cls, records):
        '''Change the state to accept another signature'''
        pass

    @classmethod
    def get_reporting_grades(cls, records, field):
        vals = {}
        for record in records:
            score = 0.0
            for section in record.sections:
                score += (section.weightage / 100 * section.average_score_reporting)
            vals[record.id] = score
        return vals

    @classmethod
    def get_reviewing_grades(cls, records, field):
        vals = {}
        for record in records:
            score = 0.0
            for section in record.sections:
                score += (section.weightage / 100 * section.average_score_reviewing)
            vals[record.id] = score
        return vals


class EmployeeFormSignature(ModelSQL, ModelView):
    "Employee Form Signature"

    __name__ = "apar.employee.form.signature"

    signed_by_user = fields.Many2One('res.user', 'Signed By', required=True)
    signed_by_employee = fields.Many2One(
        'company.employee', 'Signed By Employee')
    signed_on = fields.DateTime('Signed On', required=True)
    note = fields.Text('Remarks')
    designation = fields.Many2One('employee.designation', 'Designation')
    place = fields.Char('Place')
    employee_form = fields.Many2One('apar.employee.form', 'Employee Form', ondelete='CASCADE')
    action = fields.Selection(
        [
            ('draft', 'Draft'),
            ('no_initiation', 'No Inititation Certificate'),
            ('self_appraisal', 'Self Appraisal'),
            ('reporting_officer', 'Reporting Officer'),
            ('reviewing_officer', 'Reviewing Officer'),
            ('accepting_authority', 'Accepting Authority'),
            ('disclose', 'Disclose'),
            ('signed', 'Signed by Ratee Officer'),
            ('representation', 'Raised Representation')
        ], 'Action', required=True, readonly=True
    )

class EmployeeFormLine(ModelSQL, ModelView):
    "Employee Form Line"

    __name__ = 'apar.employee.form.line'

    question = fields.Many2One(
        'apar.form.template.question', 'Question_Link', required=True)
    question_text = fields.Text('Description')
    answer = fields.Text('Remarks', states={
           'readonly': ~Eval('is_editable')
        }, depends=['is_editable']
    )
    part = fields.Many2One('apar.employee.form.part', 'Part', ondelete='CASCADE')
    is_editable = fields.Boolean('Is Editable?')

    @staticmethod
    def default_is_editable():
        return False


class AparEmployeeFormSection(ModelSQL, ModelView):
    "Apar Employee Form Section"

    __name__ = "apar.employee.form.section"

    name = fields.Char('Name', required=True)
    number = fields.Char('Section Number', required=True)
    questions = fields.One2Many(
        'apar.employee.form.section.line', 'section', 'Descriptions')
    average_score_reporting = fields.Function(
        fields.Float('Average Score Reporting'),
        'get_average_score_reporting'
    )
    average_score_reviewing = fields.Function(
        fields.Float('Average Score Reviewing'),
        'get_average_score_reviewing'
    )
    weightage = fields.Integer('Weightage')
    part = fields.Many2One('apar.employee.form.part', 'Part', ondelete='CASCADE')

    @classmethod
    def get_average_score_reporting(cls, records, field):
        """Calculate the average of grades given by reporting officer"""
        vals = {}
        for record in records:
            grade_reporting = 0
            count = 0
            for question in record.questions:
                grade_reporting += (question.grade_reporting if 
                    question.grade_reporting else 0.0)
                count += 1
            try:
                vals[record.id] = grade_reporting / count
            except ZeroDivisionError:
                vals[record.id] = 0.0
        return vals

    @classmethod
    def get_average_score_reviewing(cls, records, field):
        """Calculate the average of grades given by reviewing officer"""
        vals = {}
        for record in records:
            grade_reviewing = 0
            count = 0
            for question in record.questions:
                grade_reviewing += (question.grade_reviewing 
                    if question.grade_reviewing else 0.0)
                count += 1
            try:
                vals[record.id] = grade_reviewing / count
            except ZeroDivisionError:
                vals[record.id] = 0.0
        return vals


class AparEmployeeFormSectionLine(ModelSQL, ModelView):
    "Apar Employee Form Section Line"

    __name__ = "apar.employee.form.section.line"

    question = fields.Many2One(
        'apar.form.template.question', 'Question_Link', required=True)
    question_text = fields.Char('Description')
    grade_reporting = fields.Float('Grades by Reporting Authority', states={
        "readonly": And(
            Eval('section.part.employee_form.reporting_officer') != Eval('context', {}).get('employee', ''),
            Eval('state') != 'reporting_officer')
        }, depends=['state', 'section'])

    grade_reviewing = fields.Float('Grades by Reviewing Authority', states={
        "readonly": And(
            Eval('section.part.employee_form.reviewing_officer') != Eval('context', {}).get('employee', ''),
            Eval('state') != 'reviewing_officer')
        }, depends=['state', 'section'])

    section = fields.Many2One('apar.employee.form.section', 'Section', ondelete='CASCADE')
    state = fields.Selection([
            (None, ''),
            ('reporting_officer', 'Reporting Officer'),
            ('reviewing_officer', 'Reviewing Officer')
        ], 'State')

    @staticmethod
    def default_state():
        return None

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
            'invalid_marks': (
            'Grades should be between 0 and 10 only')    
        })

    @classmethod
    def validate(cls, records):
        super(AparEmployeeFormSectionLine, cls).validate(records)
        for record in records:
            record.check_range()

    def check_range(self):
        "Check range between 1 and 10"
        if self.grade_reporting:
            if (self.grade_reporting < 0 or self.grade_reporting >10):
                self.raise_user_error('invalid_marks')
        if self.grade_reviewing:
            if (self.grade_reviewing < 0 or self.grade_reviewing >10):
                self.raise_user_error('invalid_marks')


class APARGenerateForms(Wizard):
    'APAR Generate Forms'
    __name__ = 'apar.generate_forms'

    start_state = 'departments'
    departments = StateView(
        'apar.generate_forms.show',
        'apar.form_wizard_department_forms', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Generate APAR Forms', 'create_forms', 'tryton-go-next',
                   default=True)
        ]
    )
    create_forms = StateTransition()
    open_ = StateAction('apar.act_apar_department')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._error_messages.update({
                'missing_template': ("Designation '%s' has no "
                    "form associated to it. Contact Administrator."),
                })

    def default_departments(self, fields):
        pool = Pool()
        estabs = pool.get('health.establishment').search(
            [
                ('admin', '=',
                 pool.get('res.user')(Transaction().user).employee)
            ]
        )
        return {
            'establishments': [x.id for x in estabs]
        }

    def create_department_forms(self):
        DepartmentForm = Pool().get('apar.department.form')
        department = self.departments.department
        this_year = datetime.today().year - 1
        vlist = [{
            'department': department.id,
            'establishment': department.establishment,
            'head': department.head,
            'date_from': datetime(this_year, 4, 1),
            'date_to': datetime(this_year + 1, 3, 31)
        }]
        self.departments.department_form = DepartmentForm.create(vlist)[0]
        department.is_apar_generated = True
        department.save()

    def get_sections(self, part):
        section_lists = []
        for section in part.sections:
            section_lists.append({
                'name': section.name,
                'number': section.number,
                'questions': [('create', [{
                        'question': q.id,
                        'question_text': q.name,
                    } for q in section.questions])],
                'weightage': section.weightage,
            })
        return section_lists

    def get_parts_list(self, posting):
        if not posting.designation.template:
            self.raise_user_error('missing_template',
                (posting.designation.name))
        template = posting.designation.template
        parts_list = []
        for part in template.parts:
            parts_list.append({
                'number': part.number,
                'name': part.name,
                'questions': [('create', [{
                        'question': q.id,
                        'question_text': q.name,
                    } for q in part.questions])],
                'is_sections': True if part.sections else False,
                'sections': [('create', self.get_sections(part))],
                'type_': part.type_ ,
            })
            
        return parts_list

    def get_postings_list(self, department):
        Posting = Pool().get('employee.posting')
        Designation = Pool().get('employee.designation')
        year = datetime.today().year - 1
        designations = Designation.search([('is_apar_generate', '=', True)])

        # Search for the postings where following condition is not satisfied - 
        #  a. date_from and date_to are both less than 1 April of current year.
        #  b. date_from and date_to are both more than 31 March of next year.
        #  Possible Cases are -
        #  a. date_from less than 1 April and date_to more than 1 april
        #  b. date_from more than 1 April and date_from less than 31 March
        postings = Posting.search(
            [
                ['OR',
                    ['AND',
                        ('date_from', '<=', datetime(year, 4, 1)),
                        ['OR',
                            ('date_to', '>=', datetime(year, 4, 1)),
                            ('date_to', '=', None)]],
                    ['AND',
                        ('date_from', '>=', datetime(year, 4, 1)),
                        ('date_from', '<', datetime(year + 1, 3, 31))]],
                ('department', '=', department.id),
                ('designation', 'in', designations)
            ]
        )
        return postings

    def create_employee_forms(self):
        pool = Pool()
        EmployeeForm = pool.get('apar.employee.form')
        User = pool.get('res.user')
        ModelData = pool.get('ir.model.data')
        ratee_officer = ModelData.get_id('apar', 'group_ratee_officer')
        vlist = []
        department = self.departments.department
        postings = self.get_postings_list(department)
        this_year = datetime.today().year - 1
        start_date = datetime(this_year, 4, 1).date()
        end_date = datetime(this_year + 1, 3, 31).date()
        for posting in postings:

            parts_list = self.get_parts_list(posting)
            employee = posting.employee

            date_from = start_date if posting.date_from < start_date else posting.date_from
            date_to = posting.date_to or end_date

            vlist.append({
                'employee_code': employee.employee_id,
                'employee': employee,
                'department_form': self.departments.department_form.id,
                'department': department,
                'date_from': date_from,
                'date_to': date_to,
                'designation': posting.designation.id,
                'date_of_birth': employee.party.dob,
                'parts': [('create', parts_list)],
                'form_name': posting.designation.template.name,
                'date_of_joining': employee.date_of_joining,
                'category': employee.category,
                'date_appointment': posting.date_from,
                'present_grade': employee.grade,
                'present_post': posting.designation.id,
                'date_posting_present_post': posting.date_from,
                'pay_in_band': employee.pay_in_band,
                'grade_pay': employee.grade_pay.id,
            })

            employee_users = User.search([
                ('employee', '=', employee)
            ])
            for employee_user in employee_users:
                employee_user_groups = list(employee_user.groups)
                if ratee_officer not in employee_user_groups:
                    employee_user_groups.append(ratee_officer)
                    employee_user.groups = employee_user_groups
                    employee_user.save()

        EmployeeForm.create(vlist)

    def transition_create_forms(self):
        self.create_department_forms()
        self.create_employee_forms()
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
            ('id', '=', self.departments.department_form.id)])
        return action, {}


class APARGenerateFormsShow(ModelView):
    'APAR Generate Department View'
    __name__ = 'apar.generate_forms.show'

    department = fields.Many2One(
        'company.department', 'Department',
        domain=[
            ('establishment', '=', Eval('establishment')),
            ('is_apar_generated', '=', False)
        ],
        depends=['establishment'], required=True
    )
    department_form = fields.Many2One(
        'apar.department.form', 'Department Form')
    establishment = fields.Many2One(
        'health.establishment', 'Establishment',
        domain=[('id', 'in', Eval('establishments'))],
        depends=['establishments'], required=True
    )
    establishments = fields.Many2Many(
        'health.establishment', None, None, 'Establishment')
