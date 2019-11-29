from trytond.model import ModelSQL, ModelView, fields
from trytond.model import Workflow
from trytond.pyson import Eval
from trytond.pool import Pool
from trytond.transaction import Transaction

__all__ = [
    'HighDegreeAllowance',
    ]


class HighDegreeAllowance(Workflow, ModelSQL, ModelView):
    'Higher Degree Qualification Allowance'

    __name__ = 'hr.allowance.hda'

    salary_code = fields.Char('Salary Code')
    employee = fields.Many2One('company.employee', 'Employee Name')
    designation = fields.Many2One('company.employee','Designation')
    department = fields.Many2One('company.employee','Department')
    hda_amount = fields.Float('Final HDA Amount',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    # qualification = fields.Selection([
    #     ('1', 'Ph.D or equivalent.'),
    #     ('2', 'PG Degree/Diploma of duration more than one year,Or equivalent.'),
    #     ('3', 'PG Degree/Diploma of duration one year or less, Or equivalent.'),
    #     ('4', 'PG Degree/Diploma of duration more than three years,Or equivalent.'),
    #     ('5', 'PG Degree/Diploma of duration three years or less,Or equivalent.'),
    #     ],    'Qualification')

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
        if self.employee:
            self.salary_code = self.employee.salary_code


    @staticmethod
    def default_employee():
        global current_employee
        current_employee = None
        pool = Pool()
        Employee = pool.get('company.employee')
        employee_id = Transaction().context.get('employee')
        employee = Employee.search([
            ('id', '=', employee_id)
        ])
        if employee != []:
            current_employee = employee[0]
        return current_employee.id if current_employee else None