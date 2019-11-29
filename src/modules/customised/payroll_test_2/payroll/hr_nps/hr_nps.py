from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.model import Workflow
from trytond.transaction import Transaction

__all__ = [
    'NpsDetails', 'Ddo', 'HrEmployee', 'NpsLine'
]


class NpsDetails(Workflow, ModelSQL, ModelView):
    'National Pension System'

    __name__ = 'npsdetails.nps'

    ddo_regno = fields.Char('DDO Registration Number')
    pran_no = fields.Integer('Pran Number')
    employee = fields.Many2One('company.employee', 'Name')
    govt_cont = fields.Float('Goverment\'s Contribution')
    sub_cont = fields.Float('Subscribers\'s Contribution')
    pay_month = fields.Char('Month')
    pay_year = fields.Char('Year')
    cont_type = fields.Selection([
        ('regular', 'Regular'),
        ('arrears', 'Arrears'),
    ], 'Contribution type')
    remarks = fields.Char('Remarks')
    code = fields.Char('Code')
    bpay = fields.Float('Basic Pay')
    npa = fields.Char('Non Practicing Allowance')
    da = fields.Char('Dearness Allowance')
    nps_no = fields.Char('National Pension Number ')
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
                'invisible': ~Eval('state').in_(
                    ['draft']),
                'depends': ['state'],
            },
            'cancel': {
                'invisible': ~Eval('state').in_(
                    ['confirm', 'draft']),
                'depends': ['state'],
            },
            'done': {
                'invisible': ~Eval('state').in_(
                    ['confirm']),
                'depends': ['state'],
            },
        })
        cls._error_messages.update({
            'pran_12_digits':
                ('PRAN NO should be in 12 digits'),
        })

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
        super(NpsDetails, cls).validate(records)
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
        if self.employee:
            if self.employee.nps_no:
                self.nps_no = self.employee.nps_no

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
            return current_employee.id
        else:
            return None


class NpsLine(ModelSQL, ModelView):
    'npsline'

    __name__ = 'npsline.nps'

    employee = fields.Many2One('company.employee', 'Name')
    designation = fields.Many2One('company.employee', 'Designation')
    department = fields.Many2One('company.employee', 'Department')
    pay_month = fields.Date('Pay Month')
    nps_deduction = fields.Float('Nps Deduction')
    amount = fields.Float('Amount')
    nps_fund = fields.Float('Nps Fund')
    payslip = fields.Many2One('hr.payslip', 'Payslip details')
    # payslip_number = fields.Many2One('hr.payslip','Payslip number')


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

    @classmethod
    def view_attributes(cls):
        super(HrEmployee, cls).view_attributes()
        nps = ~Eval('gpf_nps').in_(['nps'])
        attribute = [
            ("//page[@id='employee_nps_ddo_details']",
             "states", {"invisible": nps}),
        ]
        return attribute
