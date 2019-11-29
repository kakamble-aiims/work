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
    
    name = fields.Char('Payslip Name')
    number = fields.Char('Reference')
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    salary_code = fields.Char('Salary Code', required=True)
    structure = fields.Many2One('hr.salary.structure', 'Salary Structure', required=True)
    contract = fields.Many2One('hr.contract', 'Salary Details', required=True)
    code = fields.Integer('Code')
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
    year = fields.Integer('Year',required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Successful'),
        ('verify', 'Waiting'),
        ('cancel', 'Rejected'),
        ('paid', 'Paid'),
    ], 'Status', readonly=True, required=True)
    lines = fields.One2Many(
                'hr.payslip.line',
                'payslip', string='Payslip Lines')
    payslip_batch = fields.Many2One(
                    'hr.payslip.batch',
                    'Payslip Batches')  #batches in payslip.run
    bank_name = fields.Char('Bank Name')
    ifsc = fields.Char('IFSC Code')
    bank_address = fields.Text('Bank Address')
    account_no = fields.Integer('Account Number')
    bank_status = fields.Char('Bank Account Status')
    taxable_salary = fields.Float('Taxable Salary')
    net_salary = fields.Float('Net Salary')
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
                'paid': {
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
        super(HrPayslip,cls).validate(records)
        for record in records:
            if record.year not in range(2015,2051):
                cls.raise_user_error('Year Out of Bounds')

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
                # 'employee': self.employee.id,
                'amount': amount,
                'total':amount,
                'priority': rule.priority,
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

    name = fields.Char('Name', required=True)
    code = fields.Char('Code',required=True)
    #TODO: name, code is required
    payslip = fields.Many2One('hr.payslip', string='PaySlip',required=True)
    salary_rule = fields.Many2One('hr.salary.rule', string='Rule',required=True)
    category = fields.Many2One('hr.salary.rule.category','Category')
    amount = fields.Float('Amount', required=True)
    total = fields.Float('Total', required=True)
    priority = fields.Integer('Priority', required=True)


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
        'Salary Rules')

    def generate_pay_slip(self, employee, contract, payslip_batch=None):
        '''Generate a pay slip

        :return: A record of HR Payslip
        '''
        month = datetime.date.today().strftime("%B")
        year = datetime.date.today().year
        date_ = month +" " + str(year)
        month_no = datetime.date.today().month
        
        Payslip = Pool().get('hr.payslip')
        vals = {
            # 'number': 'SLIP-{}'.format(),
            'name': 'Salary Slip of {} for {}'.format(
                            employee.party.name, date_),
            'salary_code':employee.salary_code,
            'employee': employee,
            'structure': self,
            'contract': contract,
            'bank_name': employee.bank_name.bank if employee.bank_name.bank else None,
            'ifsc': employee.ifsc if employee.ifsc else None,
            'bank_address': employee.bank_address if employee.bank_address else None,
            'account_no': employee.account_no if employee.account_no else None,
            'bank_status': employee.bank_status,
            'month' : month_no,
            'year' : year,
            'state' :  'draft'
        }
        if payslip_batch:
            vals['payslip_batch'] = payslip_batch
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

        PayslipBatch = Pool().get('hr.payslip.batch')
        
        for record in records:
            month = datetime.date.today().strftime("%B")
            month_no = datetime.date.today().month
            year = datetime.date.today().year
            date_ = month +" " + str(year)
            # slipbatch = PayslipBatch.search([('name', '=', name)])
            # if not slipbatch:
            payslip_batch = PayslipBatch.create([{
                'name': '{} - {}'.format(record.name, date_),
                'year' : '{}'.format(year),
                'month': '{}'.format(month_no)
                # 'date_from':
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
            ('dep_away_delhi', 'Deputation outside Delhi'),
            ('dep_within_delhi', 'Deputation wihtin Delhi'),
        ], 'Deputation Status', states={
            'invisible': ~Eval('employee_status').in_(['Deputation'])
            }, depends=['employee_status'])
