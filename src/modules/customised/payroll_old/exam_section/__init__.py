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
        RenumerationSignature,
        TADASignature,
        TADAllowancePerDay,
        TADAHotelFoodEntitlement,
        ExamType,
        ExamTypeRenumerationLines,
        ExamTypeTADALines,
        Exam,
        Centers,
        Employees,
        GetTADABillView,
        GetRenumerationBillView,
        ExamTypeTADAGradePay,
        ExamTypeTaDaPayLevel,
        ExamTypePaymentBasis,
        module="exam_section", type_="model"
    )

    Pool.register(
        GetTADABill,
        GetRenumerationBill,
        module="exam_section", type_="wizard"
    )
