from trytond.pool import Pool
from .hr_exam_section import *
from .hr_exams import *
from .hr_exam_bills import *


def register():
    Pool.register(
        RenumerationBill,
        RenumerationPurposeandPay,
        TADABill,
        TADAJourney,
        TADAHotelFood,
        TADALocalTransport,
        ContingencyBill,
        ContingencyJourney,
        ExamCenter,
        TADAllowancePerDay,
        TADAHotelFoodEntitlement,
        ExamType,
        ExamTypeRenumerationLines,
        ExamTypeTADALines,
        Exam,
        Centers,
        Employees,
        ExamTypeTADAGradePay,
        ExamTypeTaDaPayLevel,
        ExamTypePaymentBasis,
        ExamTypeTADAGST,
        module="hr_exam_section", type_="model"
    )
