import datetime
from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = [
    'InvestmentScheme', 'InvestmentSection',
    'IncomeTaxSlab', 'IncomeTaxRule',
    'IncomeTaxDeduction', 'FiscalYear',
    'TaxableIncomeProjectionsLine',
]


class InvestmentScheme(ModelSQL, ModelView):
    """ Investment Schemes """

    __name__ = 'investment.scheme'

    name = fields.Char(
        'Scheme Details', help='Enter Investment Scheme'
    )
    section = fields.Many2One(
        'investment.section', 'Section', help='Select Section'
    )
    rebate_allowed = fields.Float(
        'Rebate allowed', help='Rebate allowed as per scheme'
    )


class InvestmentSection(ModelSQL, ModelView):
    """ Investment Sections """

    __name__ = 'investment.section'

    name = fields.Char(
        'Section Details', help='Enter Section'
    )
    schemes = fields.One2Many(
        'investment.scheme', 'section', 'Scheme',
        help='Select the Scheme'
    )
    allowed_limit = fields.Float(
        'Maximum amount allowed',
        help='Enter Maximum amount'
    )


class IncomeTaxSlab(ModelSQL, ModelView):
    """Income Tax slab  """

    __name__ = 'income_tax.slab'

    income_tax_rule = fields.Many2One(
        'income_tax.rule', 'IT Rule')
    from_amount = fields.Float('From')
    to_amount = fields.Float('To')
    base = fields.Float('Base')
    percentage = fields.Float('Percentage')


class IncomeTaxRule(ModelSQL, ModelView):
    """  Income Tax Rules"""

    __name__ = 'income_tax.rule'

    name = fields.Char('Rule Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    fiscal_year = fields.Many2One('account.fiscalyear', 'Fiscal Year')
    gender = fields.Selection([
        ('not_applicable', 'Not Applicable'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', "Other")], 'Gender')
    born_after = fields.Date('Born after')
    born_before = fields.Date('Born before')
    cess = fields.Integer('Cess %')
    rule_lines = fields.One2Many('income_tax.slab',
                                 'income_tax_rule',
                                 'Rules')

    @staticmethod
    def default_gender():
        '''returns gender as Not applicable default value'''
        return 'not_applicable'

    @staticmethod
    def default_fiscal_year():
        '''
        returns start_date as this year's current
        fiscal year's start_date value.
        '''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        return current_fiscal_year

    @classmethod
    def get_annual_income_tax(cls, employee, income):
        '''Calculate the income tax based on employee's record,
        current fiscal year and applicable tax slab
        '''
        projected_income_tax = 0
        taxable_income = income
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        tax_rule = pool.get('income_tax.rule')
        tax_rules = tax_rule.search([
            ('fiscal_year', '=', current_fiscal_year),
        ])
        for rule in tax_rules:
            for slab in rule.rule_lines:
                if slab.from_amount <= taxable_income and \
                        slab.to_amount >= taxable_income:
                    projected_income_tax = (slab.percentage/100)*taxable_income
                    return projected_income_tax

    @classmethod
    def get_income_tax_ytd(cls, employee, income):
        '''
        Calculate the income tax deducted based on employee's
        record, current fiscal year and applicable tax slab

        TODO: Review the docstring and method
        '''
        taxable_income_ytd = income
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        tax_rule = pool.get('income_tax.rule')
        tax_rules = tax_rule.search([
            ('fiscal_year', '=', current_fiscal_year),
        ])
        for rule in tax_rules:
            for slab in rule.rule_lines:
                if slab.from_amount <= taxable_income_ytd and \
                        slab.to_amount >= taxable_income_ytd:
                    annual_income_tax = (slab.percentage/100) \
                        * taxable_income_ytd
                    return annual_income_tax


class IncomeTaxDeduction(ModelSQL, ModelView):
    """ Income Tax projections and real outcomes """

    __name__ = 'income_tax.deduction'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    fiscal_year = fields.Many2One('account.fiscalyear', 'Fiscal Year')
    annual_salary_ytd = fields.Float(
        'Annual Salary (YTD)',
        digits=(10, 2)
    )
    annual_salary_projected = fields.Float(
        'Annual Salary (Projected)',
        digits=(10, 2)
    )
    income_from_other_source = fields.Float(
        'Income from other Sources',
        digits=(10, 2)
    )
    annual_taxable_income_ytd = fields.Float(
        'Annual Taxable Income (YTD)',
        help="Annual Taxable Income on which "
        "we calculate the income tax.",
        digits=(10, 2)
    )
    annual_taxable_income_projected = fields.Float(
        'Annual Taxable Income (Projected)',
        help="Projected Annual Taxable Income on "
        "which we calculate the income tax.",
        digits=(10, 2)
    )
    income_tax_projected = fields.Float(
        'Projected Income Tax (Before Exemption)',
        help="This is subjected to variations based on "
        "the Income Tax Declarations, change in Salary "
        "or any Govt. Rules or policies.",
        digits=(10, 2))
    tax_exemption = fields.Float(
        'Tax Exemption',
        help="Annual Tax Exemption calculated "
        "from the employee's current investment declaration.",
        digits=(10, 2)
    )
    income_tax_projected_exemption = fields.Float(
        'Projected Income Tax (After Exemption)',
        help="This is subjected to variations based on "
        "the Income Tax Declarations, change in Salary "
        "or any Govt. Rules or policies.",
        digits=(10, 2))
    income_tax_ytd = fields.Float(
        'Income Tax (Year To Date)',
        help="This is the actual TDS deducted in "
        "the current financial year.",
        digits=(10, 2))
    tds_lines = fields.One2Many(
        'income_tax.taxable_amount_lines',
        'taxable_amount_projections',
        'Projected Income Taxable Amount Lines'
    )

    # For calculation purpose only - Start
    projected_tds_lines = fields.One2Many(
        'income_tax.taxable_amount_lines',
        'taxable_amount_projections',
        'Projected Income Taxable Amount Lines',
        domain=[('state', '=', 'projected')]
    )
    deducted_tds_lines = fields.One2Many(
        'income_tax.taxable_amount_lines',
        'taxable_amount_projections',
        'Deducted Income Taxable Amount Lines',
        domain=[('state', '=', 'deducted')]
    )

    @staticmethod
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    @fields.depends('employee')
    def on_change_employee(self, name=None):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department

    @staticmethod
    def default_start_date():
        '''
        returns start_date as this year's current
        fiscal year's start_date value.
        '''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        return fiscal(current_fiscal_year).start_date \
            if current_fiscal_year else None

    @staticmethod
    def default_fiscal_year():
        '''
        returns start_date as this year's current
        fiscal year's start_date value.
        '''
        current_fiscal_year = None
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        if fiscal.find(company):
            current_fiscal_year = fiscal.find(company)
        return current_fiscal_year

    @staticmethod
    def default_end_date():
        '''
        returns end_date as this year's current
        fiscal year's end_date value.
        '''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        return fiscal(current_fiscal_year).end_date \
            if current_fiscal_year else None
    
    def get_tax_exemption(self, month, year):
        '''Get the tax exemption from the current
        year's investment declaration'''
        pool = Pool()
        tax_exemption = 0
        current_inv_declaration_1 = None
        fiscal = pool.get('account.fiscalyear')
        inv_declaration = pool.get('investment.declaration')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        current_date = datetime.date(year, int(month), 1)
        current_inv_declaration = inv_declaration.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year)
        ], order=[('write_date', 'DESC')])
        for declaration in current_inv_declaration:
            date = declaration.write_date.date()
            if date <= current_date:
                current_inv_declaration_1 = declaration
                break
        if current_inv_declaration_1:
            tax_exemption = current_inv_declaration_1.net_tax_exempted
        return tax_exemption

    def get_tds_line(self, month, year):
        '''Returns the dictionary for TDS Lines'''
        vals = {}
        for line in self.tds_lines:
            if line.month == month and line.year == year:
                vals = {
                    'tds': line.amount,
                    'state': line.state,
                }
        return vals

    def calculate_monthly_tds(self):
        '''
        get total taxed amount till date and
        add projected taxed amount plus
        the investment declaration, if any
        based on the tax slab
        for the remaining months on monthly basis
        '''
        pool = Pool()
        TaxSlab = pool.get('income_tax.rule')
        Payslip = pool.get('hr.payslip')
        PayslipLine = Pool().get('hr.payslip.line')
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        # Get payslips of current fiscal year
        payslips = Payslip.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year),
        ], order=[('year', 'ASC')])
        annual_tax = TaxSlab.get_annual_income_tax(
            self.employee,
            self.annual_taxable_income_projected
        )
        current_month = datetime.date.today().month
        tax_exemption = self.tax_exemption
        # Saving Projected Income Tax for current fiscal year
        if annual_tax:
            self.income_tax_projected = annual_tax
            self.income_tax_projected_exemption = self.income_tax_projected \
                - self.tax_exemption
        else:
            self.raise_user_error('No Income Tax Rule defined')
        if not self.tds_lines:
            # If there are no tds lines, then create the new sheet
            TDSLines = pool.get('income_tax.taxable_amount_lines')
            if payslips:
                for payslip in payslips:
                    if int(payslip.month) == current_month:
                        break
                    payslip_lines = PayslipLine.search([
                        ('payslip', '=', payslip),
                        ('salary_rule.code', '=', 'TDS')
                    ])
                    payslip_tds = payslip_lines[0] \
                        if payslip_lines else None
                    TDSLines.create([
                        {
                            'month': payslip.month,
                            'year': payslip.year,
                            'amount': round(payslip_tds.amount, 2)
                            if payslip_tds else 0,
                            'state': 'projected',
                            'taxable_amount_projections': self
                        }
                    ])
            if tax_exemption:
                monthly_tds = (annual_tax / 12) - (tax_exemption / 12)
            else:
                monthly_tds = (annual_tax / 12)
            if current_month >= 4:
                for month in range(current_month, 13):
                    TDSLines.create([
                        {
                            'month': str(month),
                            'year': datetime.date.today().year,
                            'amount': round(monthly_tds, 2),
                            'state': 'projected',
                            'taxable_amount_projections': self
                        }
                    ])
            for month in range(current_month if current_month < 4 else 1, 4):
                TDSLines.create(
                    [
                        {
                            'month': str(month),
                            'year': datetime.date.today().year + 1,
                            'amount': round(monthly_tds, 2),
                            'state': 'projected',
                            'taxable_amount_projections': self
                        }
                    ]
                )
        else:
            payslips = Payslip.search([
                ('employee', '=', self.employee),
                ('fiscal_year', '=', self.fiscal_year),
            ], order=[('year', 'ASC')])
            for payslip in payslips:
                tds_month = 0
                exemption = 0
                if int(payslip.month) == current_month:
                    break
                payslip_lines = PayslipLine.search([
                    ('payslip', '=', payslip),
                    ('salary_rule.code', '=', 'TDS')
                ])
                month = int(payslip.month)
                payslip_tds = payslip_lines[0] \
                    if payslip_lines else None
                if payslip_tds:
                    tds_month = payslip_tds.amount
                    if tds_month == 0:
                        ded = 0
                        for line in self.tds_lines:
                            if line.state == 'deducted':
                                ded += line.amount
                            else:
                                break
                        remaining_tax = annual_tax - ded
                        exemption = self.get_tax_exemption(
                            payslip.month, payslip.year
                        )
                        remaining_months = 12 \
                            if month == 4 else self.get_remaining_months(month)
                        tds = remaining_tax / remaining_months \
                            - exemption / remaining_months
                        tds_month = round(tds, 2)
                        payslip_tds.amount = tds_month
                        payslip_tds.save()
                        for line in self.tds_lines:
                            if line.month == payslip.month \
                                    and line.year == payslip.year:
                                line.amount = tds_month
                                if line.state == 'projected':
                                    line.state = 'deducted'
                                line.save()
                                break
            deducted = 0
            for line in self.tds_lines:
                if line.state == 'deducted':
                    deducted += line.amount
                else:
                    break
            remaining_tax = annual_tax - deducted
            remaining_months = self.get_remaining_months(current_month)
            remaining_monthly_tds = remaining_tax / remaining_months \
                - tax_exemption/remaining_months
            remaining_monthly_tds = round(remaining_monthly_tds, 2)
            for pline in self.tds_lines:
                if pline.state == 'projected':
                    pline.amount = remaining_monthly_tds
                    pline.save()
        # TODO: review the method for calculation button calls twice

    def calculate_income_tax_ytd(self):
        '''
        TODO: review the docstring
        '''
        pool = Pool()
        Payslip = pool.get('hr.payslip')
        PayslipLine = pool.get('hr.payslip.line')
        payslips = Payslip.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', self.fiscal_year),
        ])
        annual_tax_ytd = 0
        for payslip in payslips:
            payslip_tds = PayslipLine.search([
                ('payslip', '=', payslip),
                ('salary_rule.code', '=', 'TDS'),
            ])
            tds = payslip_tds[0].amount if payslip_tds else 0
            annual_tax_ytd += tds
        # Saving Income Tax YTD for current fiscal year
        self.income_tax_ytd = annual_tax_ytd

    def get_remaining_months(self, month):
        '''
        calculate the remaining number of months
        in the current financial year
        '''
        current_month = month
        if current_month <= 12 and current_month > 3:
            remaining_months = (12-current_month)+4
            # 3 months in the next year and 1 to include the current month
            return remaining_months
        elif current_month <= 3:
            remaining_months = (3-current_month)+1
            # 1 to include the current month
            return remaining_months

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'calculate_income_tax_sheet': {},
        })

    def calculate_income_from_other_sources(self):
        '''Get Income from other sources from Investment Decalaration'''
        '''
            Algo -
            Go to employee > current year investment_decalartion
            and get the income from other sources
        '''
        employee_investment = []
        pool = Pool()
        Investment = pool.get('investment.declaration')
        investments = Investment.search(
            [
                ('employee', '=', self.employee),
            ], order=[('write_date', 'DESC')]
        )
        if investments:
            employee_investment = investments[0]
            self.income_from_other_source = \
                employee_investment.total_income_declared
        else:
            self.income_from_other_source = 0

    def calculate_taxable_salary_ytd(self):
        '''Get taxable salary from the payslips in current fiscal year'''
        '''
            Algo -
            Go to Employee > Payslips.
            Search for current year's payslips.
            You will find the taxable income.
        '''
        pool = Pool()
        Payslip = pool.get('hr.payslip')
        fiscal = pool.get('account.fiscalyear')
        current_month = datetime.date.today().month
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        vals = [
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year),
        ]
        payslips = Payslip.search(
            vals, order=[('year', 'ASC')]
        )
        res_salary = 0
        for payslip in payslips:
            if int(payslip.month) == current_month:
                break
            res_salary += payslip.get_taxable_salary_amount()
        self.annual_salary_ytd = res_salary
        self.save()

    def calculate_taxable_salary_projected(self):
        '''
            Algo -
            1. Get the taxable salary from last month's salary slip.
            2. Multiply last salary in remaining months
            3. Add the YTD salary
        '''
        pool = Pool()
        vals = []
        current_month = datetime.date.today().month
        Payslip = pool.get('hr.payslip')
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        if current_month == 4:
            current_year = datetime.date.today().year
            current_date = datetime.date(current_year, 4, 1)
            date_prev_year = datetime.date(current_year-1, 4, 1)
            prev_fiscal_year = fiscal.search([
                ('end_date', '<', current_date),
                ('end_date', '>=', date_prev_year),
            ])
            vals = [
                ('employee', '=', self.employee),
                ('month', '=', str(current_month-1)),
                ('fiscal_year', '=', prev_fiscal_year),
            ]
        else:
            vals = [
                ('employee', '=', self.employee),
                ('month', '=', str(current_month-1)),
                ('fiscal_year', '=', current_fiscal_year),
            ]
        payslip_prev_month = Payslip.search(vals)
        global current_payslip
        res = 0
        taxable_salary_prev_month = 0
        remaining_months = self.get_remaining_months(current_month)
        if payslip_prev_month:
            current_payslip = payslip_prev_month[0]
            taxable_salary_prev_month =  \
                current_payslip.get_taxable_salary_amount()
        res = taxable_salary_prev_month * remaining_months
        payslips = Payslip.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year),
        ], order=[('year', 'ASC')])
        res_salary = 0
        for payslip in payslips:
            if int(payslip.month) == current_month:
                break
            res_salary += payslip.get_taxable_salary_amount()
        res_salary_projected = res_salary + res
        # TODO: Figure out projected salary for month of April
        self.annual_salary_projected = res_salary_projected

    def calculate_annual_taxable_income_ytd(self):
        '''Calculate annual taxable using the following formula:

        taxable salary from payslips in current fiscal year +
        income from other source
        '''

        self.annual_taxable_income_ytd = (
            self.annual_salary_ytd + self.income_from_other_source)

    def calculate_annual_taxable_income_projected(self):
        '''Calculate the projected annual taxable income:
        '''
        self.annual_taxable_income_projected = (
            self.annual_salary_projected + self.income_from_other_source)
    
    def calculate_tax_exemption(self):
        '''Get the tax exemption from the current
        year's investment declaration'''
        pool = Pool()
        tax_exemption = 0
        current_inv_declaration_1 = None
        fiscal = pool.get('account.fiscalyear')
        inv_declaration = pool.get('investment.declaration')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        current_date = datetime.date.today()
        current_inv_declaration = inv_declaration.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year)
        ], order=[('write_date', 'DESC')])
        for declaration in current_inv_declaration:
            date = declaration.write_date.date()
            if date <= current_date:
                current_inv_declaration_1 = declaration
                break
        if current_inv_declaration_1:
            tax_exemption = current_inv_declaration_1.net_tax_exempted
        self.tax_exemption = tax_exemption
        self.save()

    @classmethod
    def calculate_income_tax_sheet(cls, records):
        '''Calculate Entire Income Tax Sheet'''
        for record in records:
            record.calculate_income_from_other_sources()
            record.calculate_taxable_salary_ytd()
            record.calculate_taxable_salary_projected()
            record.calculate_annual_taxable_income_ytd()
            record.calculate_annual_taxable_income_projected()
            record.calculate_tax_exemption()
            record.calculate_income_tax_ytd()
            record.calculate_monthly_tds()
            record.save()


class FiscalYear(metaclass=PoolMeta):

    __name__ = 'account.fiscalyear'

    income_tax_assessment_year = fields.Char('Income Tax assessment year')


class TaxableIncomeProjectionsLine(ModelSQL, ModelView):
    """ Taxable Income amount per month Lines """

    __name__ = "income_tax.taxable_amount_lines"

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
        ], 'Month'
    )
    year = fields.Integer('Year')
    amount = fields.Float('Annual Taxable Amount', digits=(10, 2))
    state = fields.Selection(
        [
            ('projected', 'Projected'),
            ('deducted', 'Deducted')
        ], 'Status', readonly=True, sort=False,
        required=True
    )
    taxable_amount_projections = fields.Many2One(
        'income_tax.deduction',
        'Annual Taxable Income'
    )
