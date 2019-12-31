from datetime import datetime
from trytond.pool import Pool, PoolMeta
from trytond.model import (ModelSQL, ModelView, fields, Workflow)

__all__ = [
    'HrSalaryRule','HrPayslip'
]


class HrSalaryRule(metaclass=PoolMeta):

    __name__ = 'hr.salary.rule'

    def calculate_NPS(self, payslip, employee, contract):
        amount = 0
        doj = datetime.date(2003, 12, 31)
        if employee.date_of_joining > doj:
            amount = (0.1 * contract.basic)
        return amount


class HrPayslip(metaclass=PoolMeta):

    __name__ = 'hr.payslip'

    @classmethod
    @ModelView.button
    @Workflow.transition('paid')
    def done(cls, records):
        for record in records:
            amount = 0
            if record.employee.gpf_nps == 'nps':
                pool = Pool()
                nps_lines_data = pool.get('npsline.nps')
                vals = {
                    'date' : datetime.now().date(),
                    'nps_deduction': (record.contract.basic * 10/100),
                    'govt_contribution': (record.contract.basic * 14/100),
                    'employee' : record.employee,
                    'designation' : record.employee.designation,
                    # 'department' : record.employee.department,
                    'amount' : record.contract.basic,
                    'payslip' : record.id
                }
                print(vals, "--------"*88)
                nps_lines_data.create([vals])
        pass
