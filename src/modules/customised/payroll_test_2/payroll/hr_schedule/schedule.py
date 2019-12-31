from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'OASchedule', 'EHSSchedule', 'EHSScheduleWiz',
    'OAScheduleWiz', 'OAReport', 'EHSReport']


class OASchedule(ModelView):
    'Office Association Fund Schedule'

    __name__ = 'oa.schedule'

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


class OAScheduleWiz(Wizard):
    'Office Association Fund Schedule Wizard'

    __name__ = 'oa.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'oa.schedule',
        'hr_schedule.form_wiz_oa_view',
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
    print_report = StateReport('oa.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class OAReport(Report):

    __name__ = 'oa.report'

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
            OAReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']

        employee_list = []
        data_list = ()
        count = 0
        total_officer_fund = 0
        total_emp_fund = 0
        total_nur_fund = 0
        for record in records:
            officer_fund = 0
            nur_fund = 0
            emp_fund = 0
            for fund_data in record.lines:
                if fund_data.code == 'OA':
                    officer_fund = round(fund_data.amount)
                if fund_data.code == 'NU':
                    nur_fund = round(fund_data.amount)
                if fund_data.code == 'KU':
                    emp_fund = round(fund_data.amount)
            total_officer_fund += officer_fund
            total_nur_fund += nur_fund
            total_emp_fund += emp_fund
            count += 1
            data_list = (count, record.employee.gpf_number,
                         record.employee.party.name,
                         officer_fund, nur_fund, emp_fund)
            employee_list.append(data_list)
        report_context['oa_records'] = employee_list
        report_context['total_officer_fund'] = total_officer_fund
        report_context['total_nur_fund'] = total_nur_fund
        report_context['total_emp_fund'] = total_emp_fund
        return report_context


class EHSSchedule(ModelView):
    'EHS/EIS Schedule'

    __name__ = 'ehs.schedule'

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


class EHSScheduleWiz(Wizard):
    'EHS/EIS Schedule Wizard'

    __name__ = 'ehs.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'ehs.schedule',
        'hr_schedule.form_wiz_ehs_view',
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
    print_report = StateReport('ehs.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class EHSReport(Report):

    __name__ = 'ehs.report'

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
            EHSReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']

        employee_list = []
        data_list = ()
        count = 0
        total_eis = 0
        total_ehs = 0
        grand_total = 0
        for record in records:
            eis = 0
            ehs = 0
            total_ehs_eis = 0
            for ehs_eis_data in record.lines:
                if ehs_eis_data.code == 'EIS':
                    eis = round(ehs_eis_data.amount)
                if ehs_eis_data.code == 'EHS':
                    ehs = round(ehs_eis_data.amount)
            total_ehs_eis = round(eis + ehs)
            total_eis += eis
            total_ehs += ehs
            grand_total += total_ehs_eis
            count += 1
            data_list = (count, record.salary_code,
                         record.employee.party.name,
                         eis, ehs, total_ehs_eis)
            employee_list.append(data_list)
        report_context['ehs_records'] = employee_list
        report_context['total_eis'] = total_eis
        report_context['total_ehs'] = total_ehs
        report_context['grand_total'] = grand_total
        return report_context
