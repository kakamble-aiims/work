from trytond.model import Workflow
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrPayslipLines',
    'HRArrear', 'HrDrawn',
    ]


class HrPayslipLines(metaclass=PoolMeta):

    __name__ = 'hr.payslip.line'

    arrear_drawn = fields.Many2One('hr.arrear', 'Arrear')


class HRArrear(Workflow, ModelSQL, ModelView):
    'Arrear Calculation'

    __name__ = 'hr.arrear'

    employee = fields.Many2One(
        'company.employee', 'Employee',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    salary_code = fields.Char(
        'Salary Code',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    department = fields.Many2One(
        'company.department', 'Department',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    designation = fields.Many2One(
        'employee.designation', 'Designation',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    gpf_code = fields.Char(
        'GPF  Code',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    grade_pay = fields.Many2One(
        'company.employee.grade_pay', 'Grade Pay',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submit', 'Submit'),
        ('forward_to_ao', 'Forward to AO'),
        ('approved', 'Approved'),
        ('cancel', 'Cancel'),
        ], 'Status', readonly=True, sort=False)
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    new_basic_salary = fields.Float('New Basic Salary')
    drawn = fields.One2Many('hr.drawn', 'hrdrawn', 'Drawn Per Month')
    due = fields.One2Many('hr.payslip.line', 'arrear_drawn', 'Due Per Month')

    # @staticmethod
    # def default_employee():
    #     pool = Pool()
    #     User = pool.get('res.user')
    #     user = User(Transaction().user)
    #     employee = user.employee
    #     return employee.id if employee else None
    @fields.depends('employee')
    def on_change_employee(self, name=None):
            self.salary_code = self.employee.salary_code
            self.department = self.employee.department
            self.designation = self.employee.designation
            self.grade_pay = self.employee.grade_pay
            # self.gpf_code = self.employee.gpf_number

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'submit'),
            ('submit', 'forward_to_ao'),
            ('submit', 'cancel'),
            ('forward_to_ao', 'approved'),
            ('forward_to_ao', 'cancel'),
            ('cancel', 'cancel')
        ))
        cls._buttons.update({
                'submit': {
                    'invisible': ~Eval('state').in_(
                        ['draft']),
                    'depends': ['state'],
                    },
                "forward_to_ao": {
                    'invisible': ~Eval('state').in_(
                        ['submit',
                         ]),
                    'depends': ['state'],
                    },
                "cancel": {
                    'invisible': ~Eval('state').in_(
                        ['submit', 'forward_to_ao',
                         ]),
                    'depends': ['state'],
                    },
                "approve": {
                    'invisible': ~Eval('state').in_(
                        ['forward_to_ao',
                         ]),
                    'depends': ['state'],
                    },
                "drawn_per_month": {},
                })

    @classmethod
    @ModelView.button
    @Workflow.transition('submit')
    def submit(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('forward_to_ao')
    def forward_to_ao(cls, records):
        pass

    @classmethod
    @Workflow.transition('approved')
    def approve(cls, records):
        pass

    @classmethod
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass

    @classmethod
    def drawn_per_month(cls, records):
        '''Fetch payslip drawn per month'''

        pay = Pool().get('hr.payslip')
        bpay = 0
        da = 0
        hra = 0
        npa = 0
        trans = 0
        gross = 0
        for record in records:
            drawn_pay = pay.search([
                ('employee', '=', record.employee),
                ('month', '>=', str(record.from_date.month)),
                ('month', '<=', str(record.to_date.month)),
                ('year', '>=', record.from_date.year),
                ('year', '<=', record.to_date.year),
                ])
            for pay in drawn_pay:
                for payline in pay.lines:
                    if payline.code == 'BASIC':
                        bpay = payline.amount
                    elif payline.code == 'DA':
                        da = payline.amount
                    elif payline.code == 'HRA':
                        hra = payline.amount
                    elif payline.code == 'NPA':
                        npa = payline.amount
                    elif payline.code == 'GROSS':
                        gross = payline.amount
                    elif payline.code == 'TRANSPORT_ALW':
                        trans = payline.amount
                date_year = (pay.month + "/" + str(pay.year))
                pay_drawn = Pool().get('hr.drawn')
                if pay_drawn is not None:
                    drawn_td = pay_drawn.search([
                        ('month_year', '=', date_year)
                    ])
                    if drawn_td:
                        continue
                    else:
                        vals = {
                            'month_year': str(date_year),
                            'hrdrawn': record.id,
                            'bpay': bpay,
                            'npay': npa,
                            'da': da,
                            'hra': hra,
                            'gross': gross,
                            'trans': trans
                        }
                        pay_drawn.create([vals])


class HrDrawn(ModelSQL, ModelView):
    'Hr Drawn'

    __name__ = 'hr.drawn'

    month_year = fields.Char('month_year')
    bpay = fields.Float('BPAY')
    npay = fields.Float('NPAY')
    da = fields.Float('DA')
    hra = fields.Float('HRA')
    spay = fields.Float('SPAY')
    drpa = fields.Float('DRPA')
    cca = fields.Float('CCA')
    trans = fields.Float('TRANS')
    gross = fields.Float('GROSS')
    hrdrawn = fields.Many2One('hr.arrear', 'Arrear')
