import datetime
from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval
from trytond.model import Workflow
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

    name = fields.Char('Scheme Details',
                help='Enter Investment Scheme')
    section  = fields.Many2One('investment.section', 'Section',
                help='Select Section')
    rebate_allowed = fields.Float('Rebate allowed',
                help='Rebate allowed as per scheme')


class InvestmentSection(ModelSQL, ModelView):
    """ Investment Sections """

    __name__ = 'investment.section'

    name = fields.Char('Section Details',
                help='Enter Section')
    schemes  = fields.One2Many(
                'investment.scheme',
                'section', 'Scheme',
                help='Select the Scheme')
    allowed_limit = fields.Float('Maximum amount allowed',
                help='Enter Maximum amount')


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
        taxable_income = income
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        tax_rule = pool.get('income_tax.rule')
        tax_slab = tax_rule.search([
                ('fiscal_year', '=', current_fiscal_year),
            ])
        for slab in tax_slab:
            tax_slab = pool.get('income_tax.slab')
            slabs = tax_slab.search([
            ('from_amount', '<=', taxable_income),
            ('to_amount', '>=', taxable_income),
            ('income_tax_rule', '=', slab.id)
            ])
            for line in slabs:
                projected_income_tax = (line.percentage/100)*taxable_income
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
        tax_slab = tax_rule.search([
                ('fiscal_year', '=', current_fiscal_year),
            ])
        for slab in tax_slab:
            tax_slab = pool.get('income_tax.slab')
            slabs = tax_slab.search([
            ('from_amount', '<=', taxable_income_ytd),
            ('to_amount', '>=', taxable_income_ytd),
            ('income_tax_rule', '=', slab.id)
            ])
            for line in slabs:
                annual_income_tax = (line.percentage/100)*taxable_income_ytd
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

    annual_salary_ytd = fields.Float(
        'Annual Salary (YTD)'
    )
    annual_salary_projected = fields.Float(
        'Annual Salary (Projected)'
    )
    income_from_other_source = fields.Float(
        'Income from other Sources'
    )
    annual_taxable_income_ytd = fields.Float(
        'Annual Taxable Income (YTD)',
        help="Annual Taxable Income on which "
        "we calculate the income tax."
    )
    annual_taxable_income_projected = fields.Float(
        'Annual Taxable Income (Projected)',
        help="Projected Annual Taxable Income on "
        "which we calculate the income tax."
    )
    income_tax_projected = fields.Float(
        'Projected Income Tax',
        help="This is subjected to variations based on "
        "the Income Tax Declarations, change in Salary "
        "or any Govt. Rules or policies")
    income_tax_ytd = fields.Float(
        'Income Tax (Year To Date)',
        help="This is the actual TDS deducted in "
        "the current financial year.")
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
    # For calculation purpose only - End

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
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
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
        current_fiscal_year_id = fiscal.find(company)
        current_fiscal_year = fiscal(current_fiscal_year_id)
        return current_fiscal_year.end_date \
            if current_fiscal_year else None

    # def get_projected_tax_exemption(self):
    #     net_tax_exempted = self.get_tax_exemption()
    #     net_tax_exempted_ytd = self.get_tax_exemption_ytd()
    #     projected_tax_exemption = net_tax_exempted - net_tax_exempted_ytd
    #     return projected_tax_exemption

    def get_tax_exemption(self):
        '''Get the tax exemption from the current
        year's investment declaration'''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        inv_declaration = pool.get('investment.declaration')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        current_inv_declaration = inv_declaration.search([
           ('employee', '=', self.employee),
           ('fiscal_year', '=', current_fiscal_year)
        ], limit=1)
        if current_inv_declaration:
            current_inv_declaration_1 = current_inv_declaration[0]
        tax_exemption = current_inv_declaration_1.net_tax_exempted
        return tax_exemption

    # def get_tax_exemption_month(self, month, year):
    #     '''Get the tax exemption YTD from the current
    #     year's investment declaration'''
    #     current_date = datetime.date(year, month, 1)
    #     res = 0
    #     if month == 4:
    #         return 0
    #     else:
    #         pool = Pool()
    #         fiscal = pool.get('account.fiscalyear')
    #         declaration = pool.get('investment.declaration')
    #         Payslip = pool.get('hr.payslip')
    #         payslips = []
    #         current_fiscal_year = fiscal.search([
    #                 ('start_date', '<=', current_date),
    #                 ('end_date', '>=', current_date)
    #                 ], limit=1)
    #         if current_fiscal_year:
    #             fiscal_year = current_fiscal_year[0]
    #         if month == 5:
    #             vals = [
    #                 ('employee', '=', self.employee),
    #                 ('month', '=', str(month-1)),
    #                 ('year', '=', current_fiscal_year[0].start_date.year),
    #             ]
    #             iter_payslips = Payslip.search(vals)
    #             iter_payslip = iter_payslips[0] \
    #                 if iter_payslips else None
    #             payslips.append(iter_payslip)
    #             if payslips:

    #             print(payslips, "check"*10, count)
    #             # import pdb; pdb.set_trace()
    #         else:
    #             for iter_month in range(month):
    #                 payslip1 = Payslip.search([
    #                 ('employee', '=', self.employee),
    #                 ('month', '>=', str(iter_month)),
    #                 ('year', '=', current_fiscal_year[0].end_date.year),
    #                 ])
    #                 if payslip1:
    #                     payslips.append(payslip1[0])
    #             for iter_month in range(4, 13):
    #                 payslip2 = Payslip.search([
    #                     ('employee', '=', self.employee),
    #                     ('month', '=', str(iter_month)),
    #                     ('year', '=', current_fiscal_year[0].start_date.year),
    #                     ])
    #                 if payslip2:
    #                     payslips.append(payslip2[0])
    #         for payslip in payslips:
    #             res += payslip.get_monthly_tax_exemption()
    #     return res
    
    # def get_tax_exemption_ytd(self):
    #     '''Get the tax exemption YTD from the current
    #     year's investment declaration'''
    #     # current_date = datetime.date.today()
    #     res = 0
    #     current_month = datetime.date.today().month
    #     for month in (4, current_month):
    #         res += self.get_tax_exemption_month(month)
    #     return res
        # res = 0
        # if current_month == 4:
        #     return 0
        # else:
        #     pool = Pool()
        #     fiscal = pool.get('account.fiscalyear')
        #     declaration = pool.get('investment.declaration')
        #     Payslip = pool.get('hr.payslip')
        #     payslips = []
        #     current_fiscal_year = fiscal.search([
        #             ('start_date', '<=', current_date),
        #             ('end_date', '>=', current_date)
        #             ], limit=1)
        #     if current_fiscal_year:
        #         fiscal_year = current_fiscal_year[0]
        #     if current_month > 4:
        #         count = 0
        #         for month in range(4, current_month):
        #             vals = [
        #                 ('employee', '=', self.employee),
        #                 ('month', '=', str(month)),
        #                 ('year', '=', current_fiscal_year[0].start_date.year),
        #             ]
        #             iter_payslips = Payslip.search(vals)
        #             iter_payslip = iter_payslips[0] \
        #                 if iter_payslips else None
        #             payslips.append(iter_payslip)
        #             if payslips:
        #                 count +=1
        #             print(payslips, "check"*10, count)
        #         # import pdb; pdb.set_trace()
        #     else:
        #         for month in range(current_month):
        #             payslip1 = Payslip.search([
        #             ('employee', '=', self.employee),
        #             ('month', '>=', str(month)),
        #             ('year', '=', current_fiscal_year[0].end_date.year),
        #             ])
        #             if payslip1:
        #                 payslips.append(payslip1[0])
        #         for month in range(4, 13):
        #             payslip2 = Payslip.search([
        #                 ('employee', '=', self.employee),
        #                 ('month', '=', str(month)),
        #                 ('year', '=', current_fiscal_year[0].start_date.year),
        #                 ])
        #             if payslip2:
        #                 payslips.append(payslip2[0])
        #     for payslip in payslips:
        #         res += payslip.get_monthly_tax_exemption()

    def get_tds_line(self, month, year):
        '''Returns the dictionary for TDS Lines'''
        

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
        payslips = Payslip.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year)
        ])
            
        # import pdb; pdb.set_trace()
        annual_tax = TaxSlab.get_annual_income_tax(
            self.employee,
            self.annual_taxable_income_projected
            - self.get_tax_exemption()
        )
        print(annual_tax, "annual_tax"*8)
        # Saving Projected Income Tax for current fiscal year
        self.income_tax_projected = annual_tax
        print(self.tds_lines, "self.tds_linesself.tds_lines")
        if not self.tds_lines:
            # If there are no tds lines, then create the new sheet
            TDSLines = pool.get('income_tax.taxable_amount_lines')
            for payslip in payslips:
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
                        'amount': payslip_tds.amount \
                            if payslip_tds else 0,
                        'state': 'deducted',
                        'taxable_amount_projections': self
                    }
                ])
            monthly_tds = annual_tax / 12
            current_month = datetime.date.today().month
            if current_month >= 4:
                for month in range(current_month, 13):
                    TDSLines.create([
                        {
                            'month': str(month),
                            'year': datetime.date.today().year,
                            'amount': monthly_tds,
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
                            'amount': monthly_tds,
                            'state': 'projected',
                            'taxable_amount_projections': self
                        }
                    ]
                )
        else:
            deducted = 0
            print(self.deducted_tds_lines, "1010101010 ")
            for line in self.deducted_tds_lines:
                if line.state == 'deducted':
                    deducted += line.amount
            remaining_tax = annual_tax - deducted
            remaining_monthly_tds = (
                remaining_tax / self.get_remaining_months()
                )
            for pline in self.projected_tds_lines:
                pline.amount = remaining_monthly_tds
                pline.save()
        # TODO: review the method for calculation button calls twice

    def calculate_income_tax_ytd(self):
        '''
        TODO: review the docstring
        '''
        pool = Pool()
        TaxSlab = pool.get('income_tax.rule')
        annual_tax_ytd = TaxSlab.get_income_tax_ytd(
            self.employee,
            self.annual_taxable_income_ytd
        )

        # Saving Income Tax YTD for current fiscal year
        self.income_tax_ytd = annual_tax_ytd

    def get_remaining_months(self):
        '''
        calculate the remaining number of months
        in the current financial year
        '''
        current_month = datetime.date.today().month
        if current_month < 12 and current_month > 3:
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
        print(Investment, "hardest"*10)
        investments = Investment.search([
                # ('employee', '=', self.employee),
                ])
        print(investments, "core"*10)
        if investments:
            employee_investment = investments[0]
            print(employee_investment, "bohot hard"*10)
            print(employee_investment.total_income_declared, "employee_investment.total_income_declared"*10)
        self.income_from_other_source =  \
            employee_investment.total_income_declared
    
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
        payslips = Payslip.search(vals)
        res_salary = 0
        for payslip in payslips:
            if int(payslip.month) == current_month:
                break
            res_salary += payslip.get_taxable_salary_amount()
            # TODO: Find the taxable salary of all previous months and add
        self.annual_salary_ytd = res_salary
        self.save()

    def calculate_taxable_salary_projected(self):
        '''
            Algo - 
            1. Get the taxable salary from last month's salary slip.
            2. Multiply last salary in remaining months
            3. Add the YTD salary
        '''
        # import pdb; pdb.set_trace()
        pool = Pool()
        current_month = datetime.date.today().month
        Payslip = pool.get('hr.payslip')
        fiscal = pool.get('account.fiscalyear')
        company = Transaction().context.get('company')
        current_fiscal_year = fiscal.find(company)
        vals = [
                    ('employee', '=', self.employee),
                    ('month', '=', str(current_month-1)),
                    ('fiscal_year', '=', current_fiscal_year),
                ]
        payslip_prev_month = Payslip.search(vals)
        print(payslip_prev_month, "bohot harddd"*10)
        global current_payslip
        res = 0
        taxable_salary_prev_month = 0
        remaining_months = self.get_remaining_months()
        if payslip_prev_month:
            # print(payslip_prev_month[0], "lllllll")
            current_payslip = payslip_prev_month[0]
            taxable_salary_prev_month =  \
                current_payslip.get_taxable_salary_amount()
        res = taxable_salary_prev_month * remaining_months
        print(res, "nasha"*40)
        payslips = Payslip.search([
            ('employee', '=', self.employee),
            ('fiscal_year', '=', current_fiscal_year),
        ])
        print(payslips, "payslip for months completed"*20)
        res_salary = 0
        for payslip in payslips:
            if int(payslip.month) == current_month:
                break
            res_salary += payslip.get_taxable_salary_amount()
        print(res_salary, "pehla"*10)
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

    @classmethod
    def calculate_income_tax_sheet(cls, records):
        '''Calculate Entire Income Tax Sheet'''
        for record in records:
            record.calculate_income_from_other_sources()
            record.calculate_taxable_salary_ytd()
            record.calculate_taxable_salary_projected()
            record.calculate_annual_taxable_income_ytd()
            record.calculate_annual_taxable_income_projected()
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
    amount = fields.Float('Annual Taxable Amount')
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
