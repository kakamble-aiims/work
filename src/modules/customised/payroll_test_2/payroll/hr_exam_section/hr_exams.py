from trytond.model import ModelView, ModelSQL, fields
from trytond.pyson import Eval


__all__ = [
    'ExamType',
    'ExamTypePaymentBasis',
    'ExamTypeRenumerationLines',
    'ExamTypeTADALines',
    'ExamTypeTADAGradePay',
    'ExamTypeTaDaPayLevel',
    'ExamTypeTADAGST',
]


class ExamType(ModelSQL, ModelView):
    '''Exam Type'''

    __name__ = 'exam_section.exam_type'

    name = fields.Char('Name')
    type_exam = fields.Selection([
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate'),
        ('phd', 'PhD'),
        ('professional', 'Professional')
    ], 'Type of exam')
    payment_basis = fields.Many2One(
        'exam_section.exam_type.payment_basis',
        'Payment Basis'
    )
    active = fields.Boolean('Active')
    is_ta_applicable = fields.Boolean('Is TA/DA Applicable')
    renumeration = fields.One2Many(
        'exam_section.exam_type.renumeration',
        'exam_type', 'Renumeration Lines',
        domain=[('payment_basis', '=', 'payment_basis')]
        )
    ta_da = fields.One2Many(
        'exam_section.exam_type.ta_da',
        'exam_type',
        'TA/DA Lines'
    )

    @staticmethod
    def default_active():
        return True


class ExamTypePaymentBasis(ModelSQL, ModelView):
    '''Exam Type Payment Basis'''

    __name__ = 'exam_section.exam_type.payment_basis'

    name = fields.Char('Name')


class ExamTypeRenumerationLines(ModelSQL, ModelView):
    '''Exam Type Renumeration Lines'''

    __name__ = 'exam_section.exam_type.renumeration'

    name = fields.Char('Description')
    code = fields.Char('Code', states={
        'readonly': ~Eval('type_pay').in_(['code'])
    }, depends=['type_pay'])
    payment_basis = fields.Many2One(
        'exam_section.exam_type.payment_basis',
        'Payment Basis',
    )
    type_pay = fields.Selection([
        ('fix', 'Fix'),
        ('code', 'Code'),
    ], 'Type of pay')
    type_amount_fix = fields.Float('Fixed amount', states={
        'readonly': Eval('type_pay') != 'fix'
    }, depends=['type_pay'])
    condition_pay = fields.Selection([
        (None, ''),
        ('code', 'Code'),
        ('group', 'Group'),
        ('external', 'External'),
    ], 'Condition for Payment')
    employee_group = fields.Selection(
        [
            (None, ''),
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ], "Employee Group"
    )
    max_range = fields.Float('Maximum Amount')
    min_range = fields.Float('Minimum Amount')
    is_external = fields.Boolean(
        'Is Applicable for External'
        )
    exam_type = fields.Many2One('exam_section.exam_type', 'Exam Type')


class ExamTypeTADALines(ModelSQL, ModelView):
    '''Exam Type TA/DA Lines'''

    __name__ = 'exam_section.exam_type.ta_da'

    group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ], "Group"
    )
    grade_pays = fields.One2Many(
        'exam.type.tada_grade.pay', 'ta_da_line', 'Grade Pay')
    pay_level = fields.One2Many(
        'exam.type.tada_pay.level', 'ta_da_line', 'Pay Level')
    hotel_charges = fields.Float('Hotel Charges')
    food_charges = fields.Float('Food Charges')
    maximum = fields.Float('Max Allowed')
    minimum = fields.Float('Min Allowed')
    exam_type = fields.Many2One('exam_section.exam_type', 'Exam Type')


class ExamTypeTADAGradePay(ModelSQL, ModelView):
    """Exam Type TA DA-Grade Pay"""

    __name__ = 'exam.type.tada_grade.pay'

    grade_pay = fields.Many2One('company.employee.grade_pay', 'Grade Pay')
    ta_da_line = fields.Many2One('exam_section.exam_type.ta_da', 'TA DA Lines')


class ExamTypeTaDaPayLevel(ModelSQL, ModelView):
    """Exam Type Ta Da Pay Level"""

    __name__ = 'exam.type.tada_pay.level'
    pay_level = fields.Many2One('company.employee.grade', 'Pay Level')
    ta_da_line = fields.Many2One('exam_section.exam_type.ta_da', 'TA DA Lines')


class ExamTypeTADAGST(ModelSQL, ModelView):
    '''TA/DA Hotel GST'''

    __name__ = 'exam.type.tada_hotel.gst'

    tariff_per_night = fields.Float('Tariff Per Night')
    gst_rate = fields.Float('GST Rate')
    amount = fields.Float('Amount')
    cgst = fields.Float('CGST')
    sgst = fields.Float('SGST')
