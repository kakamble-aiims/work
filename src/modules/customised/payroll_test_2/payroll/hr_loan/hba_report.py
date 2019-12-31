from trytond.model import ModelView, fields
from trytond.report import Report
from trytond.pool import Pool
from trytond.wizard import Wizard, StateReport, StateView, Button

__all__ = [
    'HBASchedule', 'ComputerLoanScheduleWiz', 'ComputerLoanReport',
    'HBAScheduleWiz', 'HBAReport', 'ComputerLoanSchedule']


class HBASchedule(ModelView):
    'HBA Schedule'

    __name__ = 'hba.schedule'

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


class HBAScheduleWiz(Wizard):
    'HBA Schedule Wizard'

    __name__ = 'hba.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'hba.schedule',
        'hr_loan.form_wiz_hba_schedule_view',
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
    print_report = StateReport('hba.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class HBAReport(Report):

    __name__ = 'hba.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        hba_loan = Pool().get('hba.loan')
        hba_loan_data = hba_loan.search([
            ('department', '=', data['department'])
        ])
        return hba_loan_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            HBAReport, cls).get_context(records, data)
        report_context['department'] = data['department']

        employee_list = []
        count = 0
        data_list = ()
        total = 0
        for record in records:
            status = []
            for loan_data in record.loan_line:
                amount = round(loan_data.amount)
                total += amount
                status.append(loan_data.status)
            paid_install = status.count('done')
            count += 1
            data_list = (count, record.salary_code, record.employee.party.name,
                         record.designation.name, amount, paid_install, record.installment_no)
            employee_list.append(data_list)
        report_context['hba_loan_records'] = employee_list
        report_context['total'] = total
        return report_context


class ComputerLoanSchedule(ModelView):
    'Computer Loan Schedule'

    __name__ = 'computer.loan.schedule'

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


class ComputerLoanScheduleWiz(Wizard):
    'Computer Loan Schedule Wizard'

    __name__ = 'computer.loan.schedule.wiz'

    start_state = 'raises'
    raises = StateView(
        'computer.loan.schedule',
        'hr_loan.form_wiz_computer_loan_schedule_view',
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
    print_report = StateReport('computer.loan.report')

    def do_print_report(self, action):
        data = {
            'month': self.raises.month,
            'year': self.raises.year,
            'department': self.raises.department.name,
        }
        return action, data


class ComputerLoanReport(Report):

    __name__ = 'computer.loan.report'

    @classmethod
    def _get_records(cls, ids, model, data):
        computer_loan = Pool().get('computer.loan')
        computer_loan_data = computer_loan.search([
            ('department', '=', data['department'])
        ])
        return computer_loan_data

    @classmethod
    def get_context(cls, records, data):
        report_context = super(
            ComputerLoanReport, cls).get_context(records, data)
        report_context['department'] = data['department']
        report_context['month'] = data['month']
        report_context['year'] = data['year']

        employee_list = []
        count = 0
        data_list = ()
        grand_total = 0
        total = 0
        for record in records:
            status = []
            for loan_data in record.loan_line:
                amount = round(loan_data.amount)
                total += amount
                status.append(loan_data.status)
            paid_install = status.count('done')
            count += 1
            data_list = (count, record.salary_code, record.employee.party.name,
                         amount, paid_install, record.installment_no)
            employee_list.append(data_list)
        report_context['computer_loan_records'] = employee_list
        report_context['total'] = total
        return report_context
