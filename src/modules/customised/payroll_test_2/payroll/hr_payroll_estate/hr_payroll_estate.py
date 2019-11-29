from trytond.pool import Pool, PoolMeta

__all__ = ['SalaryRule']


class SalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def get_estate_details_for_employee(self, employee):
        '''Fetch employee estate details'''
        pool = Pool()
        current_estate_details_for_employee = None
        estate_table = pool.get('estate.allotment')
        employee_estate_details = estate_table.search(
            [
                ('employee', '=', employee),
                ('date_of_vacation', '=', None),
            ]
        )
        if employee_estate_details != []:
            current_estate_details_for_employee = employee_estate_details[0]
        return current_estate_details_for_employee

    def calculate_LICF(self, payslip, employee, contract):
        employee_estate_details = self.get_estate_details_for_employee(
            employee)
        amount = 0
        if employee_estate_details:
            license_fee = employee_estate_details.license_fee
            garage_fee = employee_estate_details.garage_fee
            servant_quarter_fee = employee_estate_details.servant_quarter_fee
            amount = license_fee + garage_fee + servant_quarter_fee
        return amount

    def calculate_WTR(self, payslip, employee, contract):
        amount = 0
        employee_estate_details = self.get_estate_details_for_employee(
            employee)
        if employee_estate_details:
            amount = employee_estate_details.water_charges
        return amount
