from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_Arrear(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        ota = pool.get('hr.allowance.ota')
        ot_allowance = ota.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
        ])
        if ot_allowance != []:
            employee_record = ot_allowance[0]
            amount = employee_record.amount

        return amount
