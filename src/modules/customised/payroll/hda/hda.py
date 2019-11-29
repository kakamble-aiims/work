from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow


__all__ = [
    'HDA_Allowance',
    ]


class HDA_Allowance(Workflow, ModelSQL, ModelView):
    'Higher Degree Qualification Allowance'

    __name__ = 'hda.allowance'

    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    qualification = fields.Selection([
        ('1', 'Ph.D or equivalent.'),
        ('2', 'PG Degree/Diploma of duration more than one year,) \
               or equivalent.'),
        ('3', 'PG Degree/Diploma of duration one year or less,) \
              or equivalent. '),
        ('4', 'PG Degree/Diploma of duration more than three years,) \
              or equivalent.'),
        ('5', 'PG Degree/Diploma of duration three years or less,) \
              or equivalent. '),
        ],    'Qualification', states={
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
        self.salary_code = self.employee.salary_code
