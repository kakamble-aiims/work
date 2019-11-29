from trytond.pool import Pool, PoolMeta
from datetime import date


__all__ = ['SalaryRule']


class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_CONVEYANCE_ALW(self, payslip, employee, contract):
        amount = 0
        if (employee.department == "College of Nursing" and
            employee.designation in ("lecturer", "Principal") or
            (employee.department == "Dietetics" and
                employee.designation == "Head of Department") or
            (employee.designation == "Chief Dietician",
                                     "Medical Physicist",
                                     "Senior Medical Physicist",
                                     "Senior Research Officer",
                                     "Senior Scientific Officer",
                                     "Biochemist",
                                     "Senior Biochemist",
                                     "Chemist",
                                     "Senior Chemist",
                                     "Eductionalist",
                                     "Research Officer",
                                     "Scientist I",
                                     "Scientist II",
                                     "Scientist III",
                                     "Scientist IV",
                                     "Scientist V",
                                     "Chief Librarian",
                                     "Degistrar",
                                     "Deputy Director (Computer Facility)",
                                     "System Analyst",
                                     "Senior Programmer"
                                     "Chief Technical Officer (Radiology)")):
            Conveyance = Pool().get('employee_conveyance.allowance')
            current_date = date.today()
            conveyance_alws = Conveyance.search([
                ('employee', '=', employee),
                ('state', '=', 'approve'),
                ('from_date', '<=', current_date),
                ('to_date', '>=', current_date)], limit=1)
            # TODO: Add the filter for month once the start
            # and end date are added in hr_conveyance.
            if conveyance_alws:
                amount = conveyance_alws[0].transport_amount
        return amount
