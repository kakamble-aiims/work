from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from datetime import datetime, date
from trytond.model import Workflow
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'EMBEmployeeDetails', 'EMB'
    ]

class EMBEmployeeDetails(Workflow, ModelSQL, ModelView):
    'EMB employee details'

    __name__ = 'emb.employee.details'

    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date = fields.Date('Dated', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    bill_month = fields.Char('Embalming Bill for the month of', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    emb_fee = fields.One2Many(
                        'emb.bill',
                        'bill',
                        'E.M.B Fee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
                    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('cancel_emp', 'Cancel'),
        ('f_to_hod', 'Forwarded to HoD'),
        ('f_to_ao', 'Forwarded to AO'),
        ('cancel_hod', 'Cancelled by HoD'),
        ('approve_ao', 'Approved by AO'),
        ('cancel_ao', 'Cancelled by AO')
    ], 'Status', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly=True)
    remarks = fields.Char('Remarks', states={
        'required': Eval('state').in_(['cancel_ao']),
        'invisible': ~Eval('state').in_(['cancel_ao'])
    })

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
        ('draft', 'confirm'),
        ('confirm', 'f_to_hod'),
        ('confirm', 'cancel_emp'),
        ('f_to_hod', 'f_to_ao'),
        ('f_to_hod', 'cancel_hod'),
        ('f_to_ao', 'approve_ao'),
        ('f_to_ao', 'cancel_ao'),
        ))
        cls._buttons.update({
            'submit_to_hod': {
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

    @staticmethod
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    # @fields.depends('employee')
    # def on_change_employee(self):
    #     self.salary_code=self.employee.salary_code if self.employee else ''

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department

    @classmethod
    def default_date(cls):
        present_date = datetime.now()
        return present_date    

    @classmethod
    def default_bill_month(cls):
        month = datetime.today().strftime("%B")
        return month       

class EMB(ModelSQL, ModelView):
    'E.M.B Bill of the Employee'

    __name__ = 'emb.bill'

    body_date = fields.Date('Date')
    deceased_name = fields.Char('Deceased Name')
    age = fields.Integer('Age')
    sex = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ], 'Sex')
    receipt_no = fields.Char('Cashier Vide receipt No.')
    receipt_date = fields.Date('Receipt Date')
    receipt_amount = fields.Integer('Receipt Amount Rs')
    autopsy = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], 'Autopsied \n(Y/N)')
    amount = fields.Integer('Amount Rs')
    bill = fields.Many2One(
                        'emb.employee.details',
                        'Bill'
                    )
    
    # @classmethod
    # def auto_serial_number(cls, records):
    #     """ for auto generation of serial number """

    #     count=0
    #     SerialNo = Pool().get('emb.employee.details')

    #     for records in records:
    #         count=+1
    #         Se