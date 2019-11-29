from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pyson import Eval
from datetime import *
from trytond.pool import Pool, PoolMeta
from trytond.model import Workflow

__all__ = [
    'NpsDetails', 'Ddo', 'HrEmployee', 'NpsLine'
    ]


class NpsDetails(Workflow, ModelSQL, ModelView):
    'nps'

    __name__ = 'npsdetails.nps'

    ddo_regno = fields.Char('Ddo_Regno', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    pran_no = fields.Integer('Pran_No', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee','Name', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    govt_cont = fields.Float('Govt_Con', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    sub_cont = fields.Float('Sub_Con', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    pay_month = fields.Char('Pay Month', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    pay_year = fields.Char('Pay Year', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    cont_type = fields.Selection([
        ('regular', 'Regular'),
        ('arrears', 'Arrears'),
        ],'Cont_type', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']) 
    remarks = fields.Char('Remarks', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    code = fields.Char('Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    bpay = fields.Float('Basic', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    npa = fields.Char('NPA', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    da = fields.Char('DA', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    nps_no = fields.Char('Nps No', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
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
            if(len(self.pran_no) != 12):
                self.raise_user_error('pran_12_digits')

    @fields.depends('employee')
    def on_change_employee(self):
        self.nps_no=self.employee.nps_no


class NpsLine(Workflow,ModelSQL, ModelView):    
        'npsline'
        
        __name__ = 'npsline.nps'
        
        employee = fields.Many2One('company.employee','Name', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        designation = fields.Char('Designation', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        department = fields.Char('Department', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        pay_month = fields.Date('Pay Month', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        nps_deduction = fields.Float('Nps Deduction', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        amount = fields.Float('Amount', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        nps_fund = fields.Float('Nps Fund', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        payslip = fields.Many2One('hr.payslip','Payslip details', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
        # payslip_number = fields.Many2One('hr.payslip','Payslip number')      
 
        
class HrEmployee(metaclass=PoolMeta):
    "DDO and PRAN No."

    __name__ = 'company.employee'

    ddo = fields.Many2One('nps.ddo', 'DDO')
    pran_no = fields.Integer('PRAN_NO')
    nps_no = fields.Char('NPS No')


class Ddo(ModelSQL, ModelView):
    """ DDO details """

    __name__ = 'nps.ddo'

    name = fields.Char('DDO Name')
    ddo_regno = fields.Char('DDO_REGNO')
