from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow
from trytond.pyson import Eval

__all__ = [
    'HR_Arrear',
    ]


class HR_Arrear(Workflow, ModelSQL, ModelView):
    'Arrear Calculation'

    __name__ = 'hr.arrear'

    employee_name = fields.Char('NAME')
    code = fields.Char('CODE')
    department = fields.Many2One('company.department', 'DEPARTMENT')
    designation = fields.Many2One('employee.designation', 'DESIGNATION')
    gpf_code = fields.Char('GPF CODE')
    grade_pay = fields.Char('GRADE_PAY')
