from trytond.pool import Pool, PoolMeta

__all__ = ['SalaryRule']

class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_CONVEYANCE_ALW(self, payslip, employee, contract):
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
            if self.vehicle_selection == "motor_car":
                car = 7359
                return car
            if self.vehicle_selection == "non_vehicle":
                non_vehicle = 2408
                return non_vehicle
            if self.vehicle_selection == "scooter":
                scooter = 2408
                return scooter
