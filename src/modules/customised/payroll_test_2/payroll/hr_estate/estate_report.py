from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'LicenseFeeSchedule',
    'LicenseFeeScheduleWiz', 'LicenseFeeReport']


class LicenseFeeSchedule(ModelView):
    'License Fee Schedule'

    __name__ = 'license.fee.schedule'

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


class LicenseFeeScheduleWiz(Wizard):
    'License Fee Schedule Wizard'

    __name__ = 'license.fee.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'license.fee.schedule',
        'hr_estate.form_wiz_license_fee_schedule_view',
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
    print_report = StateReport('license.fee.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class LicenseFeeReport(Report):

    __name__ = 'license.fee.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        month = int(data['month'])
        year = data['year']
        estate_allotment = Pool().get('estate.allotment')
        date = datetime.now().date()
        start_date = date.replace(year=year, month=month, day=1)
        end_date = date.replace(year=year, month=month, day=30)
        estate_data = estate_allotment.search([
            ('date_of_allocation', '>=', start_date),
            ('date_of_allocation', '<=', end_date),
            ('department', '=', data['department'])
        ])
        return estate_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            LicenseFeeReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']

        employee_list = []
        count = 0
        total_license_fee = 0
        total_water_charges = 0
        total_garage_fee = 0
        grand_total = 0
        for record in records:
            license_fee = round(record.license_fee)
            total_license_fee += license_fee
            water_charges = round(record.water_charges)
            total_water_charges += water_charges
            garage_fee = round(record.garage_fee)
            total_garage_fee += garage_fee
            total_charges = license_fee + water_charges + garage_fee
            grand_total += total_charges
            count += 1
            data_list = (count, record.salary_code, record.employee.party.name,
                         license_fee, water_charges, garage_fee, total_charges)
            employee_list.append(data_list)
        report_context['estate_records'] = employee_list
        report_context['total_license_fee'] = total_license_fee
        report_context['grand_total'] = grand_total
        report_context['total_water_charges'] = total_water_charges
        report_context['total_garage_fee'] = total_garage_fee
        return report_context
