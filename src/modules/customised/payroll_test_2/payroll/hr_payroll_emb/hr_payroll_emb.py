from trytond.pool import Pool, PoolMeta

__all__ = [
    'HrSalaryRule',
    ]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_EMB(self, payslip, employee, contract):
        amount = 0
        pool = Pool()
        emb = pool.get('emb.employee.details')
        emb_bill = emb.search([
            ('employee', '=', employee),
            ('salary_code', '=', employee.salary_code),
            # ('state', '=', 'approve')
            ])
        for emb_bills in emb_bill:
            for emb_lines in emb_bills.emb_fee:
                amount += emb_lines.amount
                return amount
            return 0
