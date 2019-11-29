from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_HDA(self, payslip, employee, contract):
        pool = Pool()
        hda = pool.get('hr.allowance.hda')
        hda_record = hda.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ('state', '=', 'approve')
        ])
        hda = 0
        if hda_record:
            basic = self.calculate_NEW_BASIC(payslip, employee, contract)
            hda = (0.24 * basic)
        return hda
