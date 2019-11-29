from trytond.model import (ModelSQL, ModelView, fields)
import datetime

__all__ = ['HrPayslipBatch']


class HrPayslipBatch(ModelSQL, ModelView):
    """ Payslip for batches """

    __name__ = 'hr.payslip.batch'

    name = fields.Char('Name', required=True)
    slips = fields.One2Many('hr.payslip', 'payslip_batch', 'Payslips')
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
        ('close', 'Close'),
    ], 'Status')

    @staticmethod
    def default_state():
        return 'draft'

    # @classmethod
    # def default_date_from(cls):
    #     start_date = datetime.date.today().replace(day=1)
    #     # y=datetime.datetime(x.year,x.month,1)
    #     return start_date

    # @classmethod
    # def default_date_to(cls):
    #     today = datetime.date.today().month
    #     end_date = datetime.date.today().replace(month=today+1, day=1)
    #     - datetime.timedelta(days=1)
    #     return end_date


