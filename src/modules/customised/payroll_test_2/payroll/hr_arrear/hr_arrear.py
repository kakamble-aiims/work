from trytond.model import Workflow
from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.report import Report

__all__ = [
    'HrPayslipLines',
    'HRArrear', 'HrDrawn', 'HrDue'
]


class HrPayslipLines(metaclass=PoolMeta):

    __name__ = 'hr.payslip.line'

    arrear_drawn = fields.Many2One('hr.arrear', 'Arrear')


class HRArrear(Workflow, ModelSQL, ModelView, Report):
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
    from_date = fields.Date(
        'From Date',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    to_date = fields.Date(
        'To Date',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    new_basic_salary = fields.Float(
        'New Basic Salary',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'], required=True)
    gross_total_drawn = fields.Float(
        'Total  Drawn Gross',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'])
    gross_total_due = fields.Float(
        'Total Due Gross',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'])
    difference = fields.Function(
        fields.Float('Difference'),
        'on_change_with_difference')
    drawn = fields.One2Many(
        'hr.drawn', 'drawn_arrear', 'Drawn Per Month',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'])
    due = fields.One2Many(
        'hr.due', 'due_arrear', 'Due Per Month',
        states={
            'readonly': Eval('state').in_(
                [
                    'submitted_to_jo', 'forward_to_ao',
                    'approved', 'cancel', 'submit',
                ]),
        }, depends=['state'])

    @fields.depends('employee')
    def on_change_employee(self, name=None):
        self.salary_code = self.employee.salary_code
        self.department = self.employee.department
        self.designation = self.employee.designation
        self.grade_pay = self.employee.grade_pay

    @fields.depends('gross_total_drawn', 'gross_total_due')
    def on_change_with_difference(self, name=None):
        if self.gross_total_due:
            difference = self.gross_total_due - self.gross_total_drawn
            return difference
        return 0

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
            "due_per_month": {},
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
    def cal_bpay(self, basic, month):
        if month[0] == str(7):
            arrear_bpay = 0
            arrear_bpay = basic + (basic * (3/100))
            rem = arrear_bpay % 10
            amount = 0
            if rem == 0:
                amount = arrear_bpay
            else:
                amount = int((arrear_bpay + 10) / 10) * 10
            self.new_basic_salary = amount
            return self.new_basic_salary
        else:
            return basic

    @classmethod
    def cal_npa(self, basic, employee):
        '''
        Takes Parameters - basic, employee designation

        returns the value of Non Practicing Allowance to be added
        '''
        if employee.designation.name in ("Scientist I",
                                         "Scientist I (Absorption)",
                                         "Scientist II",
                                         "Scientist II (Absorption)",
                                         "Scientist III",
                                         "Scientist III (Absorption)",
                                         "Scientist IV",
                                         "Scientist IV (Absorption)",
                                         "Scientist V (Absorption)",
                                         "Assistant Professor",
                                         "Associate Professor",
                                         "professor",
                                         "Lecturer",
                                         "Principal",
                                         "Director"):
            npa = (0.2 * basic)
            return npa
        else:
            npa = 0
            return npa

    @classmethod
    def cal_new_basic(self, basic, employee):
        npa = self.cal_npa(basic, employee)
        if npa:
            new_basic = npa + basic
            if new_basic > 23750:
                new_basic = 23750
            return new_basic
        else:
            new_basic = basic
            return new_basic

    @classmethod
    def cal_DA(self, basic, employee):
        '''
        Takes Parameters - employee and basic

        returns the value of Dearness Allowance to be added
        '''
        if self.cal_new_basic(basic, employee):
            dear_alw = (0.12 * self.cal_new_basic(basic, employee))
            return dear_alw
        else:
            dear_alw = (0.12 * basic)
            return dear_alw

    @classmethod
    def cal_HRA(self, basic, employee):
        arrear_drawn = Pool().get('hr.drawn')
        if arrear_drawn.hra is not None:
            hra = (0.24 * basic)
            return hra
        return None

    @classmethod
    def cal_trans(self, basic, employee):
        '''
        Takes Parameters - employee and basic

        returns the value of Transport Allowance to be added
        '''
        trans_alw = 0
        if int(employee.grade_pay.name) >= 5400:
            trans_alw = 7200 + self.cal_DA(basic, employee)
        elif int(employee.grade_pay.name) < 5400:
            trans_alw = 3600 + self.cal_DA(basic, employee)
        elif (employee.pay_in_band) > 17:
            trans_alw = 14400 + self.cal_DA(basic, employee)
        elif (employee.designation.name) == 'Centre Chief':
            trans_alw = 15750 + self.cal_DA(basic, employee)
        if employee.category == "ph":
            trans = trans_alw * 2
            trans_alw = trans
        else:
            trans_alw = trans_alw
        return trans_alw

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
        gross_sum = 0
        for record in records:
            drawn_pay = pay.search([
                ('employee', '=', record.employee),
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
                        gross = round(payline.amount)
                        gross_sum += gross
                        record.gross_total_drawn = gross_sum
                        record.save()
                    elif payline.code == 'TRANSPORT_ALW':
                        trans = payline.amount
                date_year = (pay.month + "/" + str(pay.year))
                pay_drawn = Pool().get('hr.drawn')
                drawn_td = pay_drawn.search([
                    ('month_year', '=', date_year)
                ])
                if drawn_td:
                    continue
                else:
                    vals = {
                        'month_year': str(date_year),
                        'drawn_arrear': record.id,
                        'bpay': bpay,
                        'npay': npa,
                        'da': da,
                        'hra': hra,
                        'gross': gross,
                        'trans': trans,
                        'year': pay.year,
                        'month': int(pay.month)
                    }
                    pay_drawn.create([vals])

    @classmethod
    def due_per_month(cls, records):
        '''Calculate due per month'''

        gross_sum = 0
        pay_due = Pool().get('hr.due')
        for record in records:
            for drawn_line in record.drawn:
                due_td = pay_due.search([
                    ('due_date', '=', drawn_line.month_year)
                ])
                if due_td:
                    continue
                else:
                    basic = record.new_basic_salary
                    employee = record.employee
                    bpay_data = cls.cal_bpay(basic, drawn_line.month_year)
                    npa_data = cls.cal_npa(basic, employee)
                    da_data = cls.cal_DA(basic, employee)
                    hra_data = cls.cal_HRA(basic, employee)
                    trans_data = cls.cal_trans(basic, employee)
                    gross_data = round(basic + npa_data +
                                       da_data + hra_data + trans_data)
                    gross_sum += gross_data
                    record.gross_total_due = gross_sum
                    record.save()
                    vals = {
                        'due_date': drawn_line.month_year,
                        'due_arrear': record.id,
                        'bpay': bpay_data,
                        'da': da_data,
                        'year': drawn_line.year,
                        'month': drawn_line.month,
                        'npay': npa_data,
                        'hra': hra_data,
                        'trans': trans_data,
                        'gross': gross_data,
                    }
                    pay_due.create([vals])


class HrDrawn(ModelSQL, ModelView):
    'Hr Drawn'

    __name__ = 'hr.drawn'

    month_year = fields.Char('Date')
    year = fields.Integer('Date')
    month = fields.Integer('Month')
    bpay = fields.Float('BPAY')
    npay = fields.Float('NPAY')
    da = fields.Float('DA')
    hra = fields.Float('HRA')
    trans = fields.Float('TRANS')
    gross = fields.Float('GROSS')
    drawn_arrear = fields.Many2One('hr.arrear', 'Arrear')

    @classmethod
    def __setup__(cls):
        super(HrDrawn, cls).__setup__()
        cls._order.insert(0, ('month', 'ASC'))
        cls._order.insert(0, ('year', 'ASC'))


class HrDue(ModelSQL, ModelView):
    'Hr Due'

    __name__ = 'hr.due'

    due_date = fields.Char('Date')
    year = fields.Integer('Date')
    month = fields.Integer('Month')
    bpay = fields.Float('BPAY')
    npay = fields.Float('NPAY')
    da = fields.Float('DA')
    hra = fields.Float('HRA')
    trans = fields.Float('TRANS')
    gross = fields.Float('GROSS')
    due_arrear = fields.Many2One('hr.arrear', 'Arrear')

    @classmethod
    def __setup__(cls):
        super(HrDue, cls).__setup__()
        cls._order.insert(0, ('month', 'ASC'))
        cls._order.insert(0, ('year', 'ASC'))
