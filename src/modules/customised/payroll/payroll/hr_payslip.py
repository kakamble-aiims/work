from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval
import datetime
from trytond.model import Workflow
from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrPayslip', 'HrPayslipLine',
    'SalaryRuleCategory', 'SalaryStructure',
    'StructureRule', 'SalaryBatch', 'SalaryBatchEmployee',
    'SalaryRulesDesignation', 'EmployeeDesignation', 'HrEmployee']


class HrPayslip(Workflow, ModelSQL, ModelView):
    '''Pay Slip'''

    __name__ = 'hr.payslip'

    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    structure = fields.Many2One('salary.structure', 'Structure', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    contract = fields.Many2One('hr.contract', 'Salary Details', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    code = fields.Integer('Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    name = fields.Char('name', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    number = fields.Char('Reference', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date_from = fields.Date('Date From', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date_to = fields.Date('Date To', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('done', 'Done'),
        ('cancel', 'Rejected'),
        ('confirm', 'Successful')
    ], 'Status', readonly=True)
    lines = fields.One2Many(
                'hr.payslip.line',
                'slip', string='Payslip Lines', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    pay_and_allowance = fields.One2Many(
                'hr.payslip.line',
                'slip', string='Payslip Lines',
                domain=[('category.code', 'in', ['Basic', 'Allowance','Gross','Net'])],
                states={
                    'readonly': ~Eval('state').in_(['draft'])
                },
                depends=['state']
    )
    deductions = fields.One2Many(
                'hr.payslip.line',
                'slip', string='Payslip Lines',
                domain=[('category.code', 'in', ['Deduction'])],
                states={
                    'readonly': ~Eval('state').in_(['draft'])
                },
                depends=['state'])
    details_by_salary_rule_category = fields.One2Many(
            'hr.payslip.line', 'slip',
            string='Details by Salary Rule',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    payslip_run = fields.Many2One(
                    'hr.payslip.run',
                    'Payslip Batches',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])  #batches in payslip.run
    bank_name = fields.Char('Bank Name',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly= True)
    ifsc = fields.Char('IFSC Code',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly= True)
    bank_address = fields.Text('Bank Address',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly= True)
    account_no = fields.Integer('Account Number',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly= True)
    bank_status = fields.Char('Bank Account Status',states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'], readonly= True)

    @fields.depends('employee')
    def on_change_employee(self):
        self.salary_code = self.employee.salary_code
        self.number = self
        self.bank_name = self.employee.bank_name.bank
        self.bank_address = self.employee.bank_address
        self.account_no = self.employee.account_no
        self.bank_status = self.employee.bank_status
        start_date = datetime.date.today()
        contract = Pool().get('hr.contract')
        contracts = contract.search([('employee', '=', self.employee),
        ('date_start', '<=', start_date),
        ('date_end', '>=', start_date)])

    @property
    def pay_and_allowances(self):
        allowances_lines = []
        if self.lines:
            for line in self.lines:
                if line.category.code in ['BASIC', 'ALW']:
                    allowances_lines.append(line)
        return allowances_lines

    @property
    def deductions(self):
        deductions_lines = []
        if self.lines:
            for line in self.lines:
                if line.category.code in ['DED']:
                    deductions_lines.append(line)
        return deductions_lines

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
            ('confirm', 'done'),
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
    @Workflow.transition('done')
    def done(cls, records):
        pass


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
                'slip': self.id,
                'salary_rule': rule.id,
                'category': rule.category.id,
                'employee': self.employee.id,
                'amount': amount,
                'total': amount,
                'priority': rule.priority
            }
            print (vals)
            line = PayslipLine.create([vals])

    @classmethod
    #@ModelView.button_action('payroll.payslip_line_view_tree')
    def _compute_salary(cls, records):
        pass
 
    @classmethod
    def default_date_from(cls):
        start_date = datetime.date.today().replace(day=1)
        # y=datetime.datetime(x.year,x.month,1)
        return start_date

    @classmethod
    def default_date_to(cls):
        today = datetime.date.today().month
        end_date = (datetime.date.today().replace(month=today+1, day=1)
            -datetime.timedelta(days=1))
        return end_date

    @classmethod
    def default_payslip_month_year(cls):
        month = datetime.date.today().strftime("%B")
        year = datetime.date.today().year
        date_ = month +", " + str(year)
        return date_

    @classmethod
    def validate(cls, records):
        super(HrPayslip, cls).validate(records)
        for record in records:
            if not record.salary_code:
                cls.raise_user_error('Enter Salary Code')

class HrPayslipLine(ModelSQL, ModelView):
    '''Payslip Lines'''

    __name__ = 'hr.payslip.line'

    name = fields.Char('Name')
    code = fields.Char('Code')
    #TODO: name, code is required
    slip = fields.Many2One('hr.payslip', string='Pay Slip')
    salary_rule = fields.Many2One('salary.rule', string='Rule')
    category = fields.Many2One('salaryrule.category',
                               'Category', required=True
                            )
    employee = fields.Many2One('company.employee', string='Employee')
    amount = fields.Float('Amount')
    total = fields.Float('Total')
    priority = fields.Integer('Priority')

    @classmethod
    def __setup__(cls):
        super(HrPayslipLine, cls).__setup__()
        cls._order = [
            ('priority', 'ASC'),
            ]


class SalaryRuleCategory(ModelSQL, ModelView):
    '''Salary rule category'''

    __name__ = "salaryrule.category"

    name = fields.Char('Name', required=True)
    code = fields.Char('Code', required=True)
    parent = fields.Many2One('salaryrule.category', 'Parent')
    note = fields.Text('Notes')


class SalaryStructure(ModelSQL, ModelView):
    '''Salary Structure'''

    __name__ = "salary.structure"

    name = fields.Char('Name', required=True)
    reference = fields.Char('Reference', required=True)
    parent = fields.Many2One('salary.structure', 'parent')
    code = fields.Char('Code')
    rules = fields.Many2Many(
        'structure.rule',
        'structure',
        'rule',
        'Salary Rules',
        order=[('rule.priority', 'ASC')],)
    category = fields.Many2One('salaryrule.category', 'Category')

    def generate_pay_slip(self, employee, contract, payslip_batch=None):
        '''Generate a pay slip

        :return: A record of HR Payslip
        '''

        month = datetime.date.today().strftime("%B")
        year = datetime.date.today().year
        date_ = month +" " + str(year)
        
        Payslip = Pool().get('hr.payslip')
        vals = {
            # 'number': 'SLIP-{}'.format(),
            'name': 'Salary Slip of {} for {}'.format(
                            employee.party.name, date_),
            'salary_code':employee.salary_code,
            'employee': employee,
            'structure': self,
            'contract': contract,
            'bank_name':employee.bank_name.bank,
            'ifsc':employee.ifsc,
            'bank_address':employee.bank_address,
            'account_no':employee.account_no,
            'bank_status':employee.bank_status,
        }
        if payslip_batch:
            vals['payslip_run'] = payslip_batch
        payslip = Payslip.create([vals])[0]
        return payslip


class StructureRule(ModelSQL, ModelView):
    '''Structure and Rules'''

    __name__ = "structure.rule"

    structure = fields.Many2One('salary.structure', 'Structure')
    rule = fields.Many2One('salary.rule', 'Rule')


class SalaryBatch(ModelSQL, ModelView):
    '''Salary Batch'''

    __name__ = "hr.salary.batch"

    name = fields.Char('Salary Batch')
    employees = fields.One2Many('hr.salary.batch.employee',
                                'batch',
                                'Employees'
                            )

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'generate_payslip_batch': {},
        })
    
    @classmethod
    def generate_payslip_batch(cls, records):
        '''Generate Payslip Batch'''

        PayslipBatch = Pool().get('hr.payslip.run')
        
        for record in records:
            month = datetime.date.today().strftime("%B")
            year = datetime.date.today().year
            date_ = month +" " + str(year)
            # slipbatch = PayslipBatch.search([('name', '=', name)])
            # if not slipbatch:
            payslip_batch = PayslipBatch.create([{
                'name': '{} - {}'.format(record.name, date_)
            }])[0]
            for batch_employee in record.employees:
                employee = batch_employee.employee
                contract = employee.contracts[0]
                structure = contract.structure
                salary_slip = structure.generate_pay_slip(
                    employee,
                    contract,
                    payslip_batch
                )

                salary_slip.calculate_rules()


class SalaryBatchEmployee(ModelSQL, ModelView):
    '''Salary Batch Employee'''

    __name__ = 'hr.salary.batch.employee'
    _rec_name = 'employee'

    employee = fields.Many2One('company.employee', 'Employee')
    batch = fields.Many2One('hr.salary.batch', 'Salary Batch')


class SalaryRulesDesignation(ModelSQL, ModelView):
    """ Salary rules for each designation """

    __name__ = 'hr.salary.rules.designation'

    salary_rule = fields.Many2One('salary.rule', 'Salary Rule')
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
            ('dep_away_delhi', 'Deputation outside Delhi'),
            ('dep_within_delhi', 'Deputation wihtin Delhi'),
        ], 'Deputation Status', states={
            'invisible': ~Eval('employee_status').in_(['Deputation'])
            }, depends=['employee_status'])
