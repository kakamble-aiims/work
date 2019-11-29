from trytond.model import Workflow
from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval, Bool, PYSONEncoder, If, Or, Not, And
import datetime
from trytond.model import Workflow
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['HrContract', 'HrEmployee']

class HrContract(ModelSQL, ModelView):
    """Employee Contract"""

    __name__ = 'hr.contract'
    # _rec_name='contract_ref'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee', required=True)
    name = fields.Char('Salary detail Reference', required=True)
    center = fields.Many2One('gnuhealth.institution','Center')
    department = fields.Many2One('company.department', 'Department')
    designation = fields.Many2One('employee.designation', 'Designation')
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
    notes = fields.Text('Notes')
    is_active = fields.Boolean('Active')
    basic = fields.Float('Basic Pay')
    approve_date = fields.Date('Date of Approval',
                states={
                    'invisible': ~Eval('state').in_(['approve'])
                }, depends=['state'])
    approve_by = fields.Many2One('res.user', 'Approved By',
                states={
                    'invisible': ~Eval('state').in_(['approve'])
                }, depends=['state'])

    @classmethod
    def validate(cls, records):
        super(HrContract, cls).validate(records)
        for record in records:
            record.valid_date()
            contracts = cls.search([
                ('id', '!=', record.id),
                ('employee', '=', record.employee),
                ('date_start', '<=', record.date_start),
                ('date_end', '>=', record.date_start)
                ])
        if contracts:
            cls.raise_user_error('Contract for this user already\
                    exists for the given period')

    def valid_date(self):
        if self.date_end < self.date_start:
            self.raise_user_error('Not a valid date')
    
    @fields.depends('end_date')
    def on_change_with_is_active(self):
        present_date = datetime.date.today()
        if (present_date > self.date_end):
            return False
        return True

    @classmethod
    def set_approvedby(cls, hrcontract):
        '''
        Fill the approved by and approve date field
        '''
        approve_date = datetime.datetime.now().date()
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        for contract in hrcontract:
            print(approve_date, "approve_date", user.id,"fdsfhsdgfjhgsdf", contract.date_of_contract)
            contract.approve_date = approve_date
            contract.approve_by = user.id
        cls.save(hrcontract)

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department
            self.center = self.employee.center

    @staticmethod
    def default_schedule_pay():
        return 'monthly'


    @staticmethod
    def default_employee():
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)
        employee = user.employee
        return employee.id if employee else None

    @classmethod
    def default_date_start(cls):
        start_date = datetime.date.today().replace(day=1)
        # y=datetime.datetime(x.year,x.month,1)
        return start_date


class HrEmployee(metaclass=PoolMeta):

    __name__ = 'company.employee'

    contracts = fields.One2Many('hr.contract', 'employee', 'Contract')
    #TODO: Validate that only 1 contract is active at a given time.
