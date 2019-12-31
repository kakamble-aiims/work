from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'TutionFeeSchedule',
    'TutionFeeScheduleWiz', 'TutionFeeReport']


class TutionFeeSchedule(ModelView):
    'Tution Fee Schedule'

    __name__ = 'tution.fee.schedule'

    department = fields.Many2One('company.department', 'Department')
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
        ], 'Month', sort=False)
    year = fields.Integer('Year')


class TutionFeeScheduleWiz(Wizard):
    'Tution Fee Schedule Wizard'

    __name__ = 'tution.fee.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'tution.fee.schedule',
        'hr_cea.form_wiz_tution_fee_schedule_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'Print',
                'print_report',
                'tryton-go-next',
                default=True,
            )
        ]
    )
    print_report = StateReport('tution.fee.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class TutionFeeReport(Report):

    __name__ = 'tution.fee.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        month = int(data['month'])
        year = data['year']
        cea = Pool().get('hr.allowance.cea')
        date = datetime.now().date()
        start_date = date.replace(year=year, month=month, day=1)
        end_date = date.replace(year=year, month=month, day=30)
        cea_data = cea.search([
            ('from_date', '>=', start_date),
            ('from_date', '<=', end_date),
            ('department', '=', data['department'])
        ])
        return cea_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            TutionFeeReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']
        employee_list = []
        count = 0
        tution_fee = 0
        grand_total = 0
        for record in records:
            tution_fee = round(record.amount)
            grand_total += tution_fee
            count += 1
            data_list = (count, record.salary_code, record.employee.party.name,
                         tution_fee)
            employee_list.append(data_list)
        report_context['cea_records'] = employee_list
        report_context['grand_total'] = grand_total
        return report_context
