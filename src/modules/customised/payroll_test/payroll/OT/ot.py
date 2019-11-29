from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from datetime import datetime, date
from trytond.model import Workflow

__all__ = [
    'OTEmployeeDetails', 'OTEmployeeLog'
    ]

class OTEmployeeDetails(Workflow, ModelSQL, ModelView):
    'OT Employee details'

    __name__ = 'ot.employee.details'


    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date_from = fields.Date('Date From', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date_to = fields.Date('Date From', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    duty_hrs_from = fields.Time('Duty Hrs From', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    duty_hrs_to = fields.Time('Duty Hrs To', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    ota_rate = fields.Float('OTA Rate(Per Hr)', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    vehicle_no = fields.Char('Vehicle No.', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel_emp', 'Cancel'),
        ('f_to_hod', 'Forwarded to HoD'),
        ('f_to_ro', 'Forwarded to RO'),
        ('f_to_ao', 'Forwarded to AO'),
        ('cancel_ro', 'Cancelled by RO '),
        ('cancel_hod', 'Cancelled by HoD'),
        ('approve_ao', 'Approved by AO'),
        ('cancel_ao', 'Cancelled by AO')
    ], 'Status', readonly=True)
    ot_employee_log = fields.One2Many('ot.employee.log', 'ot_employee_details', 'OT Details', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
 
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
        ('draft', 'confirm'),
        ('confirm', 'f_to_ro'),
        ('cancel', 'cancel_emp'),
        ('f_to_ro', 'f_to_hod'),
        ('f_to_hod', 'f_to_ao'),
        ('f_to_ro', 'cancel_ro'),
        ('f_to_hod', 'cancel_hod'),
        ('f_to_ao', 'approve_ao'),
        ('f_to_ao', 'cancel_ao'),
        ))
        cls._buttons.update({
            'submit_to_ro': {
                'invisible':~Eval('state').in_(
                    ['draft']),
                'depends':['state'],
                },
            'confirm': {
                'invisible':~Eval('state').in_(
                    ['draft']),
                'depends':['state'],
                }, 
            'cancel': {
                'invisible':~Eval('state').in_(
                    ['confirm']),
                'depends':['state'],
                }, 
            'cancel_submission_ro': {
                'invisible':~Eval('state').in_(
                ['f_to_ro']),
                'depends':['state'],
                },
            'submit_to_hod': {
                'invisible':~Eval('state').in_(
                ['approve_ro']),
                'depends':['state'],
                },    
            'cancel_submission_hod': {
                'invisible':~Eval('state').in_(
                ['f_to_hod']),
                'depends':['state'],
                },
            'submit_to_ao': {
                'invisible':~Eval('state').in_(
                ['approve_hod']),
                'depends':['state'],
                },
            'approve_for_ao': {
                'invisible':~Eval('state').in_(
                ['f_to_ao']),
                'depends':['state'],
                },
            'cancel_submission_ao': {
                'invisible':~Eval('state').in_(
                ['f_to_ao']),
                'depends':['state'],
                },
            })

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @ModelView.button
    @Workflow.transition('f_to_ro')
    def submit_to_ro(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('f_to_hod')
    def submit_to_hod(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('f_to_ao')
    def submit_to_ao(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass 

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel_ro')
    def cancel_submission_ro(cls, records):
        pass   
    
    @classmethod
    @ModelView.button
    @Workflow.transition('cancel_hod')
    def cancel_submission_hod(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approve_ao')
    def approve_for_ao(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel_ao')
    def cancel_submission_ao(cls, records):
        pass

class OTEmployeeLog(ModelSQL, ModelView):
    'OT Employee Log'

    __name__ = 'ot.employee.log'

    date = fields.Date('Date')
    time_from = fields.Time('Time From')
    time_to = fields.Time('Time To')
    hours = fields.TimeDelta('Hours')
    vehicle_no = fields.Char('Vehicle No.')
    ot_employee_details = fields.Many2One('ot.employee.details', 'OT Employee Details')
