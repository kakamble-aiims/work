from trytond.pool import Pool
from .hr_payslip import *
from .hr_batches import *
from .hr_salaryrules import *
from .contract import *
from .hr_tds import *


def register():
    Pool.register(
        HrPayslip,
        HrPayslipLine,
        SalaryRuleCategory,
        SalaryStructure,
        StructureRule,
        SalaryBatch,
        SalaryBatchEmployee,
        SalaryRulesDesignation,
        EmployeeDesignation,
        HrPayslipRun,
        SalaryRule,
        Contract,
        HrEmployee,
        InvestmentScheme,
        InvestmentSection,
        InvestmentDeclaration,
        InvestmentDeclarationLine,
        IncomeTaxSlab,
        IncomeTaxRule,
        module='payroll', type_='model')
