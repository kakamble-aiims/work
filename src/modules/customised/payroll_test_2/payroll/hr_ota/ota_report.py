from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'OTASchedule',
    'OTAScheduleWiz', 'OTAReport']


class OTASchedule(ModelView):
    'OTA Schedule'

    __name__ = 'ota.schedule'

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


class OTAScheduleWiz(Wizard):
    'OTA Schedule Wizard'

    __name__ = 'ota.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'ota.schedule',
        'hr_ota.form_wiz_ota_schedule_view',
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
    print_report = StateReport('ota.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class OTAReport(Report):

    __name__ = 'ota.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        month = int(data['month'])
        year = data['year']
        ota = Pool().get('hr.allowance.ota')
        date = datetime.now().date()
        start_date = date.replace(year=year, month=month, day=1)
        end_date = date.replace(year=year, month=month, day=30)
        ota_data = ota.search([
            ('from_date', '>=', start_date),
            ('from_date', '<=', end_date),
            ('department', '=', data['department'])
        ])
        return ota_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            OTAReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']

        employee_list = []
        count = 0
        grand_total = 0
        amount = 0
        for record in records:
            amount = record.amount
            grand_total += amount
            count += 1
            data_list = (count, record.salary_code,
                         record.employee.party.name, amount)
            employee_list.append(data_list)
        report_context['ota_records'] = employee_list
        report_context['grand_total'] = grand_total
        return report_context
