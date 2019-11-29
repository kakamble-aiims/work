from datetime import date
from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = [
    'InvestmentDeclaration', 'InvestmentDeclarationLine',
    'IncomeDeclaration'
    ]


class InvestmentDeclaration(ModelSQL, ModelView):
    """ Investment Declaration"""

    __name__ = 'investment.declaration'

    name = fields.Char('Reference',
        help='Enter Reference')
    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
        ('None', '')], 'Gender',
        help='Select Gender')
    pan_number = fields.Char('PAN No.')
    date_of_joining = fields.Date('Date of Joining')
    dob = fields.Date('Date of Birth')
    fiscal_year = fields.Many2One('account.fiscalyear', 'Fiscal Year')
    start_date = fields.Date('Starting Date')
    end_date = fields.Date('Ending Date')
    income_tax_assessment_year = fields.Char('Income Tax assessment year')
    declaration_lines = fields.One2Many(
        'investment_declaration.line',
        'declaration', 'Declarations',
        help='Fill the Investment Declarations')
    income_declaration_lines = fields.One2Many(
        'hr.payroll.income.decalartion',
        'declaration', 'Income Declaration',
    )
    total_income_declared = fields.Function(
        fields.Float('Total'), 'getter_amount')
    net_tax_exempted = fields.Float('Total Tax Exempted',
        help="Under Chapter VI-A of IT Act")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('awaiting_final_declaration', 'Awaiting Final Declaration'),
        ('closed', 'Closed')], 'Status',
        readonly=True, sort=False)
    # TODO: Review the state field

    @staticmethod
    def default_state():
        '''returns draft state as default value'''
        return 'draft'
    
    @staticmethod
    def default_fiscal_year():
        '''returns Current fiscal year as default value'''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        current_date = date.today()
        current_fiscal_year = fiscal.search([
                ('start_date', '<=', current_date),
                ('end_date', '>=', current_date)
                ], limit=1)
        if len(current_fiscal_year) == 1:
            return current_fiscal_year[0].id

    @classmethod
    def getter_amount(cls, incomes, names):
        total_income = {}
        income_total = 0
        for income in incomes:
            for income_line in income.income_declaration_lines:
                income_total += income_line.total_amount
            total_income[income.id] = income_total
        result = {
            'total_income_declared': total_income,
            }
        return result
    
    @staticmethod
    def default_start_date():
        '''
        returns start_date as this year's current
        fiscal year's start_date value.
        '''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        current_date = date.today()
        current_fiscal_year = fiscal.search([
                ('start_date', '<=', current_date),
                ('end_date', '>=', current_date)
                ], limit=1)
        return current_fiscal_year[0].start_date

    @staticmethod
    def default_end_date():
        '''
        returns end_date as this year's current
        fiscal year's end_date value.
        '''
        pool = Pool()
        fiscal = pool.get('account.fiscalyear')
        current_date = date.today()
        current_fiscal_year = fiscal.search([
                ('start_date', '<=', current_date),
                ('end_date', '>=', current_date)
                ], limit=1)
        return current_fiscal_year[0].end_date

    @fields.depends('fiscal_year')
    def on_change_fiscal_year(self, name=None):
        if self.fiscal_year:
            self.income_tax_assessment_year =(
                self.fiscal_year.income_tax_assessment_year)

    @staticmethod
    def default_employee():
        ''' returns the logged in employee'''
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    @fields.depends('employee')
    def on_change_employee(self):
        ''' 
        Auto filling of fields
        based on employee and fiscal year
        '''
        if self.employee:
            self.salary_code=self.employee.salary_code 
            self.pan_number=self.employee.pan_number
            self.date_of_joining=self.employee.date_of_joining
            # self.gender=self.employee.gender
            # self.dob=self.employee.dob

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'calculate_net_tax_exempted': {},
        })

    @classmethod
    def calculate_net_tax_exempted(cls, investments):
        '''Calculate Net tax exempted
        Add the section wise total amount
        consider the section wise amount and
        find the maximum rebate allowed 
        '''
        investment_total = 0
        dict_section_amount = {}
        for investment in investments:
            for line in investment.declaration_lines:
                if line.section not in dict_section_amount:
                    dict_section_amount[line.section] = line.actual_amount
                else:
                    dict_section_amount[line.section] += line.actual_amount
            for key, value in dict_section_amount.items():
                investment_total += min([key.allowed_limit, value])
            investment.net_tax_exempted = investment_total
            investment.save()


class InvestmentDeclarationLine(ModelSQL, ModelView):
    """ InvestmentDeclaration Line """

    __name__ = 'investment_declaration.line'

    declaration = fields.Many2One('investment.declaration',
                                  'Declaration',
                                   help='Select the declaration type')
    scheme = fields.Many2One('investment.scheme', 'Scheme',
                              help='Select Scheme')
    section = fields.Many2One('investment.section', 'Section',
                              help='Select Section')
    actual_amount = fields.Float('Actual Amount',
                                 help='Enter invested amount')
    remarks = fields.Char('Remarks',
                          help='Enter remarks if any')


class IncomeDeclaration(ModelSQL, ModelView):
    '''Income from other sources'''

    __name__ = 'hr.payroll.income.decalartion'

    source = fields.Selection(
        [
            ('previous_salary', 'Income from Previous Salary'),
            ('property', 'Income from Property'),
            ('royalty', 'Income from Royalty'),
            ('bank_interest', 'Bank Inerest'),
            ('honorarium', 'Honorarium'),
            ('other', 'Others'),
        ], 'Source', required=True)
    note = fields.Char('Description')
    type_ = fields.Selection(
        [
            ('monthly', 'Monthly'),
            ('annual', 'Annual')
        ], 'Type', required=True
    )
    amount = fields.Float('Amount',
        required=True)
    total_amount = fields.Float('Total Amount',
        required=True)
    tds = fields.Float('TDS Deducted',
        help="TDS Deducted from the source")
    declaration = fields.Many2One(
        'investment.declaration', 'Declaration'
        )

    @staticmethod
    def default_type_():
        return 'monthly'

    @staticmethod
    def default_amount():
        return 0

    @fields.depends('type_', 'amount', 'total_amount')
    def on_change_with_total_amount(self, name=None):
        '''
        If the income is monthly,
        then calculate the annual income
        '''
        if self.type_ == 'monthly':
            return self.amount * 12
        return self.amount

    @classmethod
    def validate(cls, records):
        super(IncomeDeclaration, cls).validate(records)
        for record in records:
            if record.amount <= 0:
                cls.raise_user_error('Invalid Amount')
