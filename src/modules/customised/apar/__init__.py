# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .template import *
from .apar import *
from .representation import *
from .configuration import *

def register():
    Pool.register(
        Department,
        AparFormTemplate,
        EmployeeDesignation,
        AparFormTemplatePart,
        AparFormTemplateSection,
        AparFormTemplateQuestions,
        AparTemplateConfiguration,
        AparEmployeeFormSectionLine,
        AparEmployeeFormSection,
        EmployeeFormLine,
        EmployeeFormSignature,
        EmployeeFormPart,
        AparDepartmentForm,
        EmployeeForms,
        AparRepresentationForm,
        AparRepresentationSignatures,
        IrModelField,
        APARGenerateFormsShow,
        APARGenerateRepShow,
        module='apar', type_='model')

    Pool.register(
        APARGenerateForms,
        APARGenerateRepRaiseWiz,
        module='apar', type_='wizard'
    )
