from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
    ]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_ICU(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        icu = pool.get('hr.allowance.icu')
        icu_allowance = icu.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        if icu_allowance != []:
            employee_record = icu_allowance[0]
            amount = employee_record.amount
        return amount
