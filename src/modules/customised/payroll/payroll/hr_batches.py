from trytond.model import (ModelSQL, ModelView, fields)
import datetime

__all__ = [
    'HrPayslipRun']


class HrPayslipRun(ModelSQL, ModelView):
    """ Payslip run for batches """

    __name__ = 'hr.payslip.run'

    name = fields.Char('Name')
    slips = fields.One2Many('hr.payslip', 'payslip_run', 'Payslips')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    designation = fields.Many2One('employee.designation', 'Designation')
    department = fields.Many2One('company.department', 'Department')
    net_salary = fields.Float('Net Salary')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('close', 'Close'),
    ], 'Status')

    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    def default_date_from(cls):
        start_date = datetime.date.today().replace(day=1)
        # y=datetime.datetime(x.year,x.month,1)
        return start_date

    @classmethod
    def default_date_to(cls):
        today = datetime.date.today().month
        end_date = (datetime.date.today().replace(month=today+1, day=1)
        - datetime.timedelta(days=1))
        return end_date

