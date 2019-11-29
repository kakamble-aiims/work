from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
    ]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_HRA(self, payslip, employee, contract):
        if not self.calculate_LICF(payslip, employee, contract):
            hra = (0.24 * contract.basic)
            return hra
        return None
