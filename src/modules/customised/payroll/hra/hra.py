from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.model import Workflow
from trytond.pyson import Eval

__all__ = [
    'HRA_Allowance',
    ]


class HRA_Allowance(Workflow, ModelSQL, ModelView):
    'Higher Degree Qualification Allowance'

    __name__ = 'hra.allowance'

    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    designation = fields.Char('Designation', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date = fields.Date('Date', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    address = fields.Char('House Address', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    rent = fields.Float('Expenditure On Rent', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('cash_section_officer', 'Cash Section_officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
            
        ], 'Status', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "submit": {
                'invisible': ~Eval('state').in_(
                    ['draft'
                     ]),
            },
            
            "cancel": {
                'invisible': ~Eval('state').in_(
                    ['cash_section_officer'
                     ]),
            },


            "approve": {
                'invisible': ~Eval('state').in_(
                    ['cash_section_officer'
                     ]),
                
            },

            
        })
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('confirm', 'submit'),
            ('submit', 'cash_section_officer'),
            ('cash_section_officer', 'approve'),
            ('cash_section_officer', 'cancel'),
            ))
            
    @staticmethod
    def default_state():
        return 'draft'

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cash_section_officer')
    def submit(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approve')
    def approve(cls, records):
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        pass



    @fields.depends('employee')
    def on_change_employee(self):
        self.salary_code=self.employee.salary_code    