from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
    ]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_NEWS_BILL(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        newspaper = pool.get('newspaper.bill')
        news_allowance = newspaper.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ])
        if news_allowance != []:
            employee_record = news_allowance[0]
            amount = employee_record.amount
        return amount

    def calculate_TELE_BILL(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        telephone = pool.get('telephone.bill')
        tele_allowance = telephone.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            ])
        if tele_allowance != []:
            employee_record = tele_allowance[0]
            amount = employee_record.amount
        return amount
