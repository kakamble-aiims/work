from trytond.pool import Pool, PoolMeta
import datetime

__all__ = ['HrSalaryRule']


class HrSalaryRule(metaclass=PoolMeta):
    'Salary Rule'

    __name__ = 'hr.salary.rule'

    def get_exam_details_for_employee(self, employee):
        '''Fetch employee exam details'''
        pool = Pool()
        employee_current_exam_details = None
        current_exam = None
        exam_table = pool.get('exam_section.exam')
        exam_employee_table = pool.get('exam.employees')
        current_year = datetime.date.today().year
        start_date = datetime.date(current_year, 1, 1)
        end_date = datetime.date.today()
        exam_details = exam_table.search(
            [
                ('date_from', '>=', start_date),
                ('date_to', '<=', end_date),
                ('state', '=', 'final_process'),
            ], order=[('create_date', 'DESC')]
        )
        if exam_details != []:
            for current_exam in exam_details:
                employee_current_exam = exam_employee_table.search(
                    [
                        ('employee', '=', employee),
                        ('exam', '=', current_exam)
                    ]
                )
                if employee_current_exam:
                    employee_current_exam_details = employee_current_exam[0]
        return employee_current_exam_details

    def calculate_HONR(self, payslip, employee, contract):
        amount = 0
        employee_exam = self.get_exam_details_for_employee(employee)
        if employee_exam:
            renumeration_amount = employee_exam.renumeration_bill.net_amount \
                if employee_exam.renumeration_bill else 0
            # ta_da_amount = employee_exam.ta_da_bill.total_amount \
            #     if employee_exam.ta_da_bill else 0
            amount = renumeration_amount  # + ta_da_amount
        return amount
