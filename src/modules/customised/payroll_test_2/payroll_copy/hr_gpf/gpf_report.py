from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'GPFSchedule',
    'GPFScheduleWiz', 'GPFReport']


class GPFSchedule(ModelView):
    'GPF Schedule'

    __name__ = 'gpf.schedule'

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


class GPFScheduleWiz(Wizard):
    'GPF Schedule Wizard'

    __name__ = 'gpf.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'gpf.schedule',
        'hr_gpf.form_wiz_gpf_schedule_view',
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
    print_report = StateReport('gpf.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class GPFReport(Report):

    __name__ = 'gpf.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        payslip = Pool().get('hr.payslip')
        payslip_data = payslip.search([
            ('month', '>=', data['month']),
            ('year', '<=', data['year']),
            ('department', '=', data['department'])
        ])
        return payslip_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            GPFReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']

        employee_list = []
        data_list = ()
        count = 0
        gpf_sub = 0
        total = 0
        gpf_rec = 0
        total_gpf_sub = 0
        total_gpf_rec = 0
        grand_total = 0
        for record in records:
            if record.employee.gpf_nps == 'gpf':
                for gpf_data in record.lines:
                    if gpf_data.code == 'GPF':
                        gpf_sub = round(gpf_data.amount)
                    if gpf_data.code == 'GPFR':
                        gpf_rec = round(gpf_data.amount)
                total_gpf_sub += gpf_sub
                total_gpf_rec += gpf_rec
                total = gpf_sub + gpf_rec
                grand_total += total
                count += 1
                data_list = (count, record.employee.gpf_number, record.employee.party.name, gpf_sub, gpf_rec, total)
                employee_list.append(data_list)
        report_context['gpf_records'] = employee_list
        report_context['total_gpf_sub'] = total_gpf_sub
        report_context['total_gpf_rec'] = total_gpf_rec
        report_context['grand_total'] = grand_total
        return report_context
