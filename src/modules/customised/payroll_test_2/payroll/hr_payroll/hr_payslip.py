from trytond.model import (ModelSQL, ModelView, fields, Workflow)
from trytond.transaction import Transaction
import datetime
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
import xlsxwriter


__all__ = [
    'HrPayslip', 'HrPayslipLine',
    'SalaryRuleCategory', 'SalaryStructure',
    'StructureRule', 'SalaryBatch', 'SalaryBatchEmployee',
    'SalaryRulesDesignation', 'EmployeeDesignation', 'HrEmployee']


class HrPayslip(Workflow, ModelSQL, ModelView):
    '''Pay Slip'''

    __name__ = 'hr.payslip'

    name = fields.Char('Payslip Name')
    number = fields.Char('Reference')
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    salary_code = fields.Char('Salary Code', required=True)
    structure = fields.Many2One(
        'hr.salary.structure', 'Salary Structure', required=True
    )
    contract = fields.Many2One(
        'hr.contract', 'Salary Details', required=True
    )
    code = fields.Integer('Code')
    fiscal_year = fields.Many2One(
        'account.fiscalyear', 'Fiscal Year', required=True
    )
    month = fields.Selection(
        [
            ('1', 'January'),
            ('2', 'February'),
            ('3', 'March'),
            ('4', 'April'),
            ('5', 'May'),
            ('6', 'June'),
            ('7', 'July'),
            ('8', 'August'),
            ('9', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December')
        ], 'Month', required=True
    )
    year = fields.Integer('Year', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Successful'),
        ('paid', 'Paid'),
        ('verify', 'Waiting'),
        ('cancel', 'Rejected'),
    ], 'Status', readonly=True)
    total_gross_amount = fields.Function(
        fields.Float('Total Gross Amount'),
        'get_total_gross_amount'
    )
    lines = fields.One2Many(
        'hr.payslip.line',
        'payslip', string='Payslip Lines',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state']
    )
    details_by_salary_rule_category = fields.One2Many(
        'hr.payslip.line', 'payslip',
        string='Details by Salary Rule', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
    )
    payslip_batch = fields.Many2One(
        'hr.payslip.batch',
        'Payslip Batches',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
    )
    bank_name = fields.Char(
        'Bank Name',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly=True
    )
    department = fields.Many2One('company.department', 'Department')
    employee_group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('All', 'All')
        ], "Employee Group", sort=False)
    ifsc = fields.Char(
        'IFSC Code',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly=True
    )
    bank_address = fields.Text(
        'Bank Address',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly=True
    )
    account_no = fields.Char(
        'Account Number',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly=True
    )
    bank_status = fields.Char('Bank Account Status', states={
        'readonly': ~Eval('state').in_(['draft'])
    },
        depends=['state'], readonly=True)
    taxable_salary = fields.Float('Taxable Salary')
    net_salary = fields.Float('Net Salary')
    tds = fields.Float('TDS')

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.department = self.employee.department
            self.bank_name = self.employee.bank_name.bank if self.employee.bank_name else None
            self.bank_address = self.employee.bank_address
            self.account_no = self.employee.account_no
            self.bank_status = self.employee.bank_status
            self.employee_group = self.employee.employee_group

    def get_pay_and_allowances(self):
        allowances_lines = []
        if self.lines:
            for line in self.lines:
                if line.category.code in ['BASIC', 'ALW']:
                    allowances_lines.append(line)
        return allowances_lines

    def get_deductions(self):
        deductions_lines = []
        if self.lines:
            for line in self.lines:
                if line.category.code in ['DED']:
                    deductions_lines.append(line)
        return deductions_lines

    def get_total_gross_amount(self):
        res = 0
        allowances = self.get_pay_and_allowances()
        if allowances:
            for salary_rule in allowances:
                res += salary_rule.amount \
                    if salary_rule.amount else 0
        return res

    def get_total_deduction_amount(self):
        res = 0
        deductions = self.get_deductions()
        if deductions:
            for salary_rule in deductions:
                res += salary_rule.amount \
                    if salary_rule.amount else 0
        return res

    def get_taxable_salary_amount(self):
        return self.get_total_gross_amount()  \
            - self.get_total_deduction_amount()
        # review
        # TODO: Deduct tax exemption

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._order = [
            ('salary_code', 'ASC'),
        ]
        cls._transitions |= set((
            ('draft', 'verify'),
            ('verify', 'confirm'),
            ('confirm', 'paid'),
            ('confirm', 'cancel'),
            ('verify', 'cancel'),
        ))
        cls._buttons.update({
            'verify': {
                'invisible': ~Eval('state').in_(
                    ['draft']),
                'depends': ['state'],
            },
            'cancel': {
                'invisible': ~Eval('state').in_(
                    ['confirm', 'verify']),
                'depends': ['state'],
            },
            'confirm': {
                'invisible': ~Eval('state').in_(
                    ['verify']),
                'depends': ['state'],
            },
            'done': {
                'invisible': ~Eval('state').in_(
                    ['confirm']),
                'depends': ['state'],
            },
        })

    @classmethod
    @ModelView.button
    @Workflow.transition('verify')
    def verify(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('paid')
    def done(cls, records):
        pass

    @classmethod
    def validate(cls, records):
        super(HrPayslip, cls).validate(records)
        for record in records:
            if record.year not in range(2015, 2051):
                cls.raise_user_error('Year Out of Bounds')
            if not record.salary_code:
                cls.raise_user_error('Enter Salary Code')

    def calculate_rules(self):
        structure = self.structure
        PayslipLine = Pool().get('hr.payslip.line')
        for rule in structure.rules:
            condition = rule.check(self, self.employee, self.contract,)
            if not condition:
                continue
            amount = rule.calculate(
                self, self.employee, self.contract,
            )
            vals = {
                'name': rule.name,
                'code': rule.code,
                'payslip': self.id,
                'salary_rule': rule.id,
                'category': rule.category.id,
                'amount': amount,
                'total': amount,
                'priority': rule.priority,
            }
            line = PayslipLine.create([vals])

    @classmethod
    def _compute_salary(cls, records):
        pass

    @classmethod
    def default_date_from(cls):
        start_date = datetime.date.today().replace(day=1)
        return start_date

    @classmethod
    def default_date_to(cls):
        today = datetime.date.today()
        today_month = today.month
        next_month = today.replace(month=today_month+1, day=1)
        end_date = (next_month - datetime.timedelta(days=1))
        return end_date

    @fields.depends('month', 'year')
    def on_change_with_fiscal_year(self):
        current_fiscal_year = None
        if self.month and self.year:
            current_date = \
                datetime.date(self.year, int(self.month), 1)
            Fiscal = Pool().get('account.fiscalyear')
            vals = [
                ('start_date', '<=', current_date),
                ('end_date', '>=', current_date),
            ]
            fiscal_years = Fiscal.search(vals)
            if fiscal_years:
                current_fiscal_year = fiscal_years[0].id
        return current_fiscal_year

    @classmethod
    def default_payslip_month_year(cls):
        month = datetime.date.today().strftime("%B")
        year = datetime.date.today().year
        date_ = month + ", " + str(year)
        return date_


class HrPayslipLine(ModelSQL, ModelView):
    '''Payslip Lines'''

    __name__ = 'hr.payslip.line'

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    # TODO: name, code is required
    payslip = fields.Many2One('hr.payslip', string='PaySlip', ondelete='CASCADE')
    salary_rule = fields.Many2One(
        'hr.salary.rule', string='Rule', required=True
    )
    category = fields.Many2One('hr.salary.rule.category', 'Category')
    amount = fields.Float('Amount')
    # TODO: amount, total required
    total = fields.Float('Total')
    priority = fields.Integer('Priority', required=True)
    payslip_report = fields.Many2One('hr.payslip', string='PaySlip')
    tds = fields.Float('TDS')

    @classmethod
    def __setup__(cls):
        super(HrPayslipLine, cls).__setup__()
        cls._order.insert(0, ('priority', 'ASC'))


class SalaryRuleCategory(ModelSQL, ModelView):
    '''Salary rule category'''

    __name__ = "hr.salary.rule.category"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    parent = fields.Many2One('hr.salary.rule.category', 'Parent')
    note = fields.Text('Note')


class SalaryStructure(ModelSQL, ModelView):
    '''Salary Structure'''

    __name__ = "hr.salary.structure"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code')
    parent = fields.Many2One('hr.salary.structure', 'parent')
    rules = fields.Many2Many(
        'hr.salary.structure-hr.salary.rule',
        'structure',
        'rule',
        'Salary Rules',
        order=[('rule.priority', 'ASC')],
    )

    def generate_pay_slip(self, employee, contract, payslip_batch=None):
        '''Generate a pay slip

        :return: A record of HR Payslip
        '''
        month = datetime.date.today().strftime("%B")
        year = datetime.date.today().year
        date_ = month + " " + str(year)
        month_no = datetime.date.today().month
        Fiscal = Pool().get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = Fiscal.find(company)
        Payslip = Pool().get('hr.payslip')
        vals = {
            'name': 'Salary Slip of {} for {}'.format(
                employee.party.name, date_),
            'salary_code': employee.salary_code,
            'employee': employee,
            'structure': self.id,
            'contract': contract,
            'bank_name': employee.bank_name.bank
            if employee.bank_name else None,
            'ifsc': employee.ifsc if employee.ifsc else None,
            'bank_address': employee.bank_address
            if employee.bank_address else None,
            'account_no': employee.account_no
            if employee.account_no else None,
            'bank_status': employee.bank_status,
            'month': str(month_no),
            'year': year,
            'fiscal_year': current_fiscal_year,
            'department': employee.department,
            'state': 'draft',
            'employee_group': employee.employee_group
        }
        if payslip_batch:
            vals['payslip_batch'] = payslip_batch
        payslip = Payslip.create([vals])[0]
        return payslip

    def generate_pay_slip_for_ytd(
            self, employee, contract, given_month, payslip_batch=None
    ):
        '''Generate a pay slip

        :return: A record of HR Payslip
        '''
        year = datetime.date.today().year
        month = datetime.datetime(year, given_month, 1).strftime("%B")
        date_ = month + " " + str(year)
        month_no = str(given_month)
        Fiscal = Pool().get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = Fiscal.find(company)
        Payslip = Pool().get('hr.payslip')
        vals = {
            'name': 'Salary Slip of {} for {}'.format(
                employee.party.name, date_),
            'salary_code': employee.salary_code,
            'employee': employee,
            'structure': self,
            'contract': contract,
            'bank_name': employee.bank_name.bank
            if employee.bank_name.bank else None,
            'ifsc': employee.ifsc if employee.ifsc else None,
            'bank_address': employee.bank_address
            if employee.bank_address else None,
            'account_no': employee.account_no
            if employee.account_no else None,
            'bank_status': employee.bank_status,
            'month': str(month_no),
            'year': year,
            'fiscal_year': current_fiscal_year,
            'state':  'draft',
            'employee_group': employee.employee_group
        }
        if payslip_batch:
            vals['payslip_batch'] = payslip_batch.id
        payslip = Payslip.create([vals])[0]

        return payslip


class StructureRule(ModelSQL, ModelView):
    '''Structure and Rules'''

    __name__ = "hr.salary.structure-hr.salary.rule"

    structure = fields.Many2One('hr.salary.structure', 'Structure')
    rule = fields.Many2One('hr.salary.rule', 'Rule')


class SalaryBatch(ModelSQL, ModelView):
    '''Salary Batch'''

    __name__ = "hr.salary.batch"

    name = fields.Char('Salary Batch', required=True)
    employees = fields.One2Many(
        'hr.salary.batch.employee',
        'batch',
        'Employees'
    )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'batch_excel_workbook': {},
            'generate_payslip_batch': {},
            'generate_payslip_batch_ytd': {},
        })

    @classmethod
    def generate_payslip_batch(cls, records):
        '''Generate Payslip Batch'''

        PayslipBatch = Pool().get('hr.payslip.batch')

        for record in records:
            month = datetime.date.today().strftime("%B")
            month_no = datetime.date.today().month
            year = datetime.date.today().year
            date_ = month + " " + str(year)
            payslip_batch = PayslipBatch.create([{
                'name': '{} - {}'.format(record.name, date_),
                'year': '{}'.format(year),
                'month': '{}'.format(month_no)
            }])[0]
            for batch_employee in record.employees:
                employee = batch_employee.employee
                if employee.contracts:
                    contract = employee.contracts[0]
                else:
                    cls.raise_user_error(
                        employee.party.name, 'have no salary details')
                structure = contract.structure
                salary_slip = structure.generate_pay_slip(
                    employee,
                    contract,
                    payslip_batch
                )
                salary_slip.calculate_rules()

    @classmethod
    def generate_payslip_batch_ytd(cls, records):
        '''Generate Payslip Batch'''

        PayslipBatch = Pool().get('hr.payslip.batch')
        month_no = datetime.date.today().month
        year = datetime.date.today().year
        for record in records:
            for iter_month in range(4, month_no):
                month = datetime.datetime(year, iter_month, 1).strftime("%B")
                date_ = month + " " + str(year)
                payslip_batch = PayslipBatch.create([{
                    'name': '{} - {}'.format(record.name, date_),
                    'year': '{}'.format(year),
                    'month': '{}'.format(iter_month)
                }])[0]
                for batch_employee in record.employees:
                    employee = batch_employee.employee
                    contract = employee.contracts[0]
                    structure = contract.structure
                    salary_slip = structure.generate_pay_slip_for_ytd(
                        employee,
                        contract,
                        iter_month,
                        payslip_batch
                    )
                    salary_slip.calculate_rules()

    @classmethod
    def batch_excel_workbook(cls, records):
        workbook = xlsxwriter.Workbook('test.xlsx')
        worksheet = workbook.add_worksheet()
        PayslipRule = Pool().get('hr.salary.rule')
        PayslipRules = PayslipRule.search([])
        col = 1
        row = 0
        rule_name = []
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1})
        worksheet.write('A1', 'Employee', header_format)
        for rule in PayslipRules:
            worksheet.write(0, col, rule.name, header_format)
            col += 1
            rule_name.append(rule.name)
        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        for record in records:
            for employee in record.employees:
                Payslip = Pool().get('hr.payslip')
                Payslips = Payslip.search([
                    ('employee', '=', employee.employee)
                ])
                if Payslips != []:
                    PayslipLine = Pool().get('hr.payslip.line')
                    PayslipLines = PayslipLine.search(
                        [('payslip', '=', Payslips[0])]
                    )
                    worksheet.write(row, 0, employee.employee.party.name)
                    col = 1
                    for rule in rule_name:
                        for line in PayslipLines:
                            if line.salary_rule:
                                if rule == line.salary_rule.name:
                                    worksheet.write(row, col, line.amount)
                        col += 1
                row += 1
        workbook.close()


class SalaryBatchEmployee(ModelSQL, ModelView):
    '''Salary Batch Employee'''

    __name__ = 'hr.salary.batch.employee'
    _rec_name = 'employee'

    employee = fields.Many2One('company.employee', 'Employee', required=True)
    batch = fields.Many2One('hr.salary.batch', 'Salary Batch', required=True)


class SalaryRulesDesignation(ModelSQL, ModelView):
    """ Salary rules for each designation """

    __name__ = 'hr.salary.rules.designation'

    salary_rule = fields.Many2One('hr.salary.rule', 'Salary Rule')
    is_applicable = fields.Boolean('Is applicable')
    amount = fields.Float('Enter Amount')
    designation = fields.Many2One('employee.designation', 'Designation')


class EmployeeDesignation(metaclass=PoolMeta):

    __name__ = 'employee.designation'

    salary_rules_designation = fields.One2Many(
        'hr.salary.rules.designation',
        'designation',
        'Salary rules on Designation')


class HrEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    dep_status = fields.Selection(
        [
            (None, ''),
            ('dep_away_delhi', 'Deputation outside Delhi'),
            ('dep_within_delhi', 'Deputation wihtin Delhi'),
        ], 'Deputation Status',
        states={
            'invisible': ~Eval('employee_status').in_(['Deputation'])
        }, depends=['employee_status']
    )
