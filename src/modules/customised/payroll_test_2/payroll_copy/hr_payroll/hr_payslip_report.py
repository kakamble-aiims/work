
from trytond.pool import Pool
from trytond.report import Report
from datetime import datetime
from trytond.model import ModelView, fields
from trytond.wizard import Wizard, StateReport, StateView, Button


__all__ = [
    'PayslipReport', 'IncomeTaxSchedule',
    'IncomeTaxScheduleWiz', 'IncomeTaxReport'
]


class PayslipReport(Report):

    __name__ = 'payslip_report'

    @classmethod
    def get_context(cls, records, data):
        report_context = super().get_context(records, data)
        report_context['allowances'] = cls.get_allowances(data)
        report_context['deductions'] = cls.get_deductions(data)
        report_context['gross'] = cls.get_gross(data)
        report_context['total_deductions'] = cls.get_total_deductions(data)
        report_context['net_pay'] = cls.net_pay(data)
        report_context['month_year'] = cls.month_year(data)
        return report_context

    @classmethod
    def get_allowances(cls, data):
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        allowances_list = []
        for line in payslip.lines:
            if line.category.code in ('BASIC', 'ALW', 'REM'):
                amount = "{:.2f}".format(line.amount)
                allownace_list = (line.name, amount)
                allowances_list.append(allownace_list)
        return allowances_list

    @classmethod
    def get_deductions(cls, data):
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        deductions_list = []
        for line in payslip.lines:
            if line.category.code in ('DED'):
                amount = "{:.2f}".format(line.amount)
                deduction_data = (line.name, amount)
                deductions_list.append(deduction_data)
        return deductions_list

    @classmethod
    def get_gross(cls, data):
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        gross = 0
        for line in payslip.lines:
            if line.category.code in ('GROSS'):
                gross = "{:.2f}".format(line.amount)
        return gross

    @classmethod
    def get_total_deductions(cls, data):
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        total_deduction = 0
        for line in payslip.lines:
            if line.category.code in ('DED'):
                total_deduction += line.amount
        return "{:.2f}".format(total_deduction)

    @classmethod
    def net_pay(self, data):
        gross = self.get_gross(data)
        deductions = self.get_total_deductions(data)
        net_pay = 0
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        for line in payslip.lines:
            if line.category.code in ('REM'):
                rem = line.amount
                net_pay = (float(gross)+rem) - float(deductions)
                return "{:.2f}".format(net_pay)

    @classmethod
    def month_year(self, data):
        Payslip = Pool().get('hr.payslip')
        payslip = Payslip(data.get('id'))
        year = payslip.year
        month = datetime.strptime(payslip.month, '%m').strftime("%B")
        month_year = month + ", " + str(year)
        return month_year


class IncomeTaxSchedule(ModelView):
    'Income Tax Schedule'

    __name__ = 'income.tax.schedule'

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


class IncomeTaxScheduleWiz(Wizard):
    'Income Tax Schedule Wizard'

    __name__ = 'bank.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'income.tax.schedule',
        'hr_payroll.form_wiz_income_tax_schedule_view',
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
    print_report = StateReport('income.tax.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class IncomeTaxReport(Report):

    __name__ = 'income.tax.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        month = int(data['month'])
        year = data['year']
        income_tax = Pool().get('income_tax.deduction')
        date = datetime.now().date()
        start_date = date.replace(year=year, month=month, day=1)
        end_date = date.replace(year=year, month=month, day=30)
        income_tax_data = income_tax.search([
            ('start_date', '>=', start_date),
            ('start_date', '<=', end_date),
            ('department', '=', data['department'])
        ])
        return income_tax_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            IncomeTaxReport, cls).get_context(records, data)
        report_context['month'] = datetime.strptime(
            data['month'], '%m').strftime("%B")
        report_context['year'] = data['year']
        report_context['department'] = data['department']
        employee_list = []
        count = 0
        income_tax = 0
        grand_total = 0
        for record in records:
            income_tax = record.income_tax_projected
            grand_total += income_tax
            count += 1
            data_list = (count, record.salary_code, record.employee.party.name,
                         record.designation.name, round(income_tax))
            employee_list.append(data_list)
        report_context['income_tax_records'] = employee_list
        report_context['grand_total'] = round(grand_total)
        return report_context
