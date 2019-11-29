from trytond.pool import Pool

from .hr_contract import *

def register():	
	Pool.register(
        HrContract,
        HrEmployee,
        module='contract', type_='model')

