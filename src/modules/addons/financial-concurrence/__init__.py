from trytond.pool import Pool
from .financial_checklist import *
def register():
    Pool.register(
        AccountConcurrenceChecklist,
        AccountConcurrenceChecklistLine,
        AccountConcurrenceChecklistLineItem,
        FinancialConcurrenceStage,
        module='financial_concurrence_checklist', type_='model')
