from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_HRA(self, payslip, employee, contract):
        pool = Pool()
        hra = pool.get('hr.allowance.hra')
        hra_record = hra.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
        ])
        hra = 0
        if hra_record:
            basic = self.calculate_NEW_BASIC(payslip, employee, contract)
            hra = (0.24 * basic)
        return hra
