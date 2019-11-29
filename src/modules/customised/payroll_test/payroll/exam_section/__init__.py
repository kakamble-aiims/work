from trytond.pool import Pool
from .exam_section import *
from .exams import *
from .exam_bills import *

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
        module="exam_section", type_="model"
    )
