from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
    ]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_CEA(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        cea = pool.get('hr.allowance.cea')
        cea_allowance = cea.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
            ])
        if cea_allowance != []:
            employee_record = cea_allowance[0]
            amount = employee_record.amount
        return amount
