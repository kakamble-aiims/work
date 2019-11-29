from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval
from datetime import datetime

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
        pattern_for_year_matching = "%{}".format(datetime.now().year)
        exam_details = exam_table.search(
            [
                ('name', 'like', pattern_for_year_matching),
                ('employees', '=', employee),
            ]
        )
        if exam_details != []:
            current_exam = exam_details[0]
            employee_current_exam_details = exam_employee_table.search(
                [
                    ('employee', '=', employee),
                    ('exam', '=', current_exam)
                ]
            )[0]
        return employee_current_exam_details
    
    def calculate_HONR(self, payslip, employee, contract):
        employee_exam = self.get_exam_details_for_employee(employee)
        renumeration_amount = employee_exam.renumeration_bill.net_amount
        ta_da_amount = employee_exam.ta_da_bill.total_amount
        amount = renumeration_amount + ta_da_amount
        return amount