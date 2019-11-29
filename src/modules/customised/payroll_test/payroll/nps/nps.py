from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pyson import Eval
from datetime import *
from trytond.pool import Pool, PoolMeta
from trytond.model import Workflow
from trytond.transaction import Transaction

__all__ = [
    'NpsDetails', 'Ddo', 'HrEmployee', 'NpsLine'
    ]


class NpsDetails(Workflow, ModelSQL, ModelView):
    'National Pension System'

    __name__ = 'npsdetails.nps'


    _NPS_STATES = {
        'readonly': ~Eval('state').in_(['draft'])
    }
    _REMARKS_STATE = {
        'invisible': Eval('state').in_(['draft'])
    }
    _DEPENDS = ['state']
    
    ddo_regno = fields.Char(
        'DDO Registration Number', states=_NPS_STATES, depends=_DEPENDS
    )
    pran_no = fields.Char(
        'Pran Number', states=_NPS_STATES, depends=_DEPENDS
    )
    employee = fields.Many2One(
        'company.employee', 'Name', states=_NPS_STATES,
        depends=_DEPENDS
    )
    govt_cont = fields.Float(
        'Goverment\'s Contribution', states=_NPS_STATES,
        depends=_DEPENDS
    )
    sub_cont = fields.Float(
        'Subscribers\'s Contribution', states=_NPS_STATES,
        depends=_DEPENDS
    )
    pay_month = fields.Char('Month', states=_NPS_STATES,
        depends=_DEPENDS
    )
    pay_year = fields.Char('Year', states=_NPS_STATES,
        depends=_DEPENDS
    )
    cont_type = fields.Selection([
        ('regular', 'Regular'),
        ('arrears', 'Arrears'),
        ],'Contribution type',
        states=_NPS_STATES, depends=_DEPENDS
    ) 
    remarks = fields.Char(
        'Remarks', states=_REMARKS_STATE, depends=_DEPENDS
    )
    code = fields.Char(
        'Code', states=_NPS_STATES, depends=_DEPENDS
    )
    bpay = fields.Float(
        'Basic Pay', states=_NPS_STATES, depends=_DEPENDS
    )
    npa = fields.Char(
        'Non Practicing Allowance', states=_NPS_STATES,
        depends=_DEPENDS
    )
    da = fields.Char(
        'Dearness Allowance', states=_NPS_STATES, depends=_DEPENDS
    )
    nps_no = fields.Char(
        'National Pension Number', states=_NPS_STATES, depends=_DEPENDS
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confrim'),
        ('cancel', 'Cancel'),
        ('done', 'Done')
    ], 'Status', readonly=True)


    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('draft', 'cancel'),
            ('confirm', 'done'),
            ('confirm', 'cancel'),
            ))
        cls._buttons.update({
            'confirm': {
                'invisible':~Eval('state').in_(
                    ['draft']),
                'depends':['state'],
                },
            'cancel': {
                'invisible':~Eval('state').in_(
                ['confirm', 'draft']),
                'depends':['state'],
                },
            'done': {
                'invisible':~Eval('state').in_(
                ['confirm']),
                'depends':['state'],
                },    
            })
        cls._error_messages.update({
            'pran_12_digits':
                ('PRAN NO should be in 12 digits'),
            })

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, records):
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
    @Workflow.transition('done')
    def done(cls, records):
        pass
    
    @classmethod
    def default_pay_month(cls):
        start_month = datetime.today().strftime("%B")
        return str(start_month)

    @classmethod
    def default_pay_year(cls):
        start_year = datetime.today().year
        return str(start_year)

    @classmethod
    def validate(cls, records):
        super(NpsDetails ,cls).validate(records)
        for record in records:
            record.check_pran_no()

    @staticmethod
    def default_state():
        return 'draft'

    def check_pran_no(self):
        'Check length of Pran No.'
        if self.pran_no:
            if len(self.pran_no) != 12:
                self.raise_user_error('pran_12_digits')
    
    def check_group(self):
        if self.employee and self.employee.employee_group not in ['A']:
            if self.npa:
                self.raise_user_error(
                    'Employee is not in Group A, so he cannot receive \
                    Non Practising Allowance'
                )

    @fields.depends('employee')
    def on_change_employee(self):
        self.nps_no=self.employee.nps_no

    @staticmethod
    def default_employee():
        pool = Pool()
        Employee = pool.get('company.employee')
        employee_id = Transaction().context.get('employee')
        employee = Employee.search([
            ('id', '=', employee_id)
        ])
        if employee != []:
            current_employee = employee[0]
        return current_employee.id if current_employee else None
    


class NpsLine(Workflow,ModelSQL, ModelView):    
    'npsline'
    
    __name__ = 'npsline.nps'

    employee = fields.Many2One('company.employee','Name')
    designation = fields.Many2One('employee.designation','Designation')
    department = fields.Many2One('company.department','Department')
    pay_month = fields.Date('Pay Month')
    nps_deduction = fields.Float('Nps Deduction')
    amount = fields.Float('Amount')
    nps_fund = fields.Float('Nps Fund')
    payslip = fields.Many2One('hr.payslip','Payslip details')
    # payslip_number = fields.Many2One('hr.payslip','Payslip number')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.designation = self.employee.designation if self.employee.designation else None
            self.department = self.employee.department if self.employee.department else None
 

class Ddo(ModelSQL, ModelView):
    """ DDO details """

    __name__ = 'nps.ddo'

    name = fields.Char('DDO Name')
    ddo_regno = fields.Char('DDO_REGNO')


class HrEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    ddo = fields.Many2One('nps.ddo', 'DDO')
    pran_no = fields.Integer('PRAN_NO')
    nps_no = fields.Char('NPS No')
