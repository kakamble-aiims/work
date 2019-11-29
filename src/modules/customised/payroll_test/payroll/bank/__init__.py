from trytond.pool import Pool
from .bank import *

def register():	
	Pool.register(
        BankDetails,
        HrEmployee,
        module='bank', type_='model')
