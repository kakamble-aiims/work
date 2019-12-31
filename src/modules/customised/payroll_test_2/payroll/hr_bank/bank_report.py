from trytond.model import ModelView, fields
from trytond.report import Report
from datetime import datetime
from trytond.pool import Pool
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'BankStatementSchedule',
    'BankStatementScheduleWiz', 'BankStatementReport']


class BankStatementSchedule(ModelView):
    'Bank Statement Schedule'

    __name__ = 'bank.statement.schedule'

    employee_group = employee_group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
            ('All', 'All')
        ], "Employee Group", sort=False)
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
    department = fields.Many2One('company.department', 'Department')


class BankStatementScheduleWiz(Wizard):
    'Bank Statement Schedule Wizard'

    __name__ = 'bank.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'bank.statement.schedule',
        'hr_bank.form_wiz_bank_statement_schedule_view',
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
    print_report = StateReport('bank.statement.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'employee_group': self.raises.employee_group,
            'department': self.raises.department.name,
        }
        return action, data


class BankStatementReport(Report):

    __name__ = 'bank.statement.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        payslip = Pool().get('hr.payslip')
        payslip_data = payslip.search([
            ('employee_group', '=', data['employee_group']),
            ('month', '=', data['month']),
            ('year', '=', data['year']),
            ('department', '=', data['department'])
        ])
        return payslip_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            BankStatementReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']
        report_context['employee_group'] = data['employee_group']
        employee_list = []
        count = 0
        basic = 0
        gross = 0
        deductions = 0
        grand_total = 0
        for record in records:
            count += 1
            for line in record.lines:
                if line.category.code == 'BASIC':
                    basic = line.amount
                elif line.category.code == 'GROSS':
                    gross = line.amount
                elif line.category.code == 'DED':
                    deductions += line.amount
                    net_pay = gross-deductions
            data_list = (count, record.ifsc, record.account_no, round(
                basic), record.employee.party.name, round(net_pay))
            employee_list.append(data_list)
        report_context['bank_records'] = employee_list
        for employee in employee_list:
            grand_total += employee[5]
        report_context['grand_total'] = round(grand_total)
        return report_context
