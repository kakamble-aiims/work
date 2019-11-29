from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval
import datetime
from trytond.model import Workflow
from trytond.pool import Pool, PoolMeta

__all__ = [
    'InvestmentScheme', 'InvestmentSection',
    'InvestmentDeclaration', 'InvestmentDeclarationLine',
    'IncomeTaxSlab', 'IncomeTaxRule']


class InvestmentScheme(ModelSQL, ModelView):
    """ Investment Schemes """

    __name__ = 'investment.scheme'

    name = fields.Char('Scheme Details')
    section  = fields.Many2One('investment.section', 'Section')


class InvestmentSection(ModelSQL, ModelView):
    """ Investment Sections """

    __name__ = 'investment.section'

    name = fields.Char('Section Details')
    schemes  = fields.One2Many('investment.scheme', 'section', 'Scheme')
    allowed_limit = fields.Float('Maximum amount allowed')


class InvestmentDeclaration(ModelSQL, ModelView):
    """ Investment Declaration"""

    __name__ = 'investment.declaration'

    name = fields.Char('Reference')
    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('others', 'Others'),
        ('None', '')], 'Gender')
    pan_no = fields.Char('PAN No.')
    date_of_joining = fields.Date('Date of Joining')
    dob = fields.Date('Date of Birth')
    fiscal_year = fields.Many2One('account.fiscalyear', 'Fiscal Year')
    start_date = fields.Date('Starting Date')
    end_date = fields.Date('Ending Date')
    assessment_year = fields.Date('Assessment year') #TODO: fetch start and end date
    declaration_lines = fields.One2Many('investment_declaration.line', 'declaration', 'Declarations')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('awaiting_approval', 'Awaiting Approval'),
        ('approved', 'Approved'),
        ('awaiting_final_declaration', 'Awaiting Final Declaration'),
        ('closed', 'Closed')], 'State')


class InvestmentDeclarationLine(ModelSQL, ModelView):
    """ InvestmentDeclaration Line """

    __name__ = 'investment_declaration.line'

    declaration = fields.Many2One('investment.declaration', 'Declaration')
    scheme = fields.Many2One('investment.scheme', 'Scheme')
    section = fields.Many2One('investment.section', 'Section')
    actual_amount = fields.Float('Actual Amount')
    remarks = fields.Char('Remarks')


class IncomeTaxSlab(ModelSQL, ModelView):
    """Income Tax slab  """

    __name__ = 'income_tax.slab'

    income_tax_rule = fields.Many2One('income_tax.rule', 'IT Rule')
    from_amount = fields.Integer('From')
    to_amount = fields.Integer('To')
    base = fields.Float('Base')
    percentage = fields.Float('Percentage')


class IncomeTaxRule(ModelSQL, ModelView):
    """  Income Tax Rules"""

    __name__ = 'income_tax.rule'

    name = fields.Char('Rule Name')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    gender = fields.Selection([
        ('not_applicable', 'Not Applicable'),
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', "Other")], 'Gender')
    born_after = fields.Date('Born after')
    born_before = fields.Date('Born before')
    cess = fields.Integer('Cess %')
    rule_lines = fields.One2Many('income_tax.slab', 'income_tax_rule', 'Rules')
