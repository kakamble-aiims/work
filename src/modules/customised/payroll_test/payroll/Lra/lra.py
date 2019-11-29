from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval, Bool
import datetime
from trytond.model import Workflow


__all__ = [
    'LR_Allowance',
    ]


class LR_Allowance(Workflow, ModelSQL, ModelView):
    'Learning Resource Allowance'

    __name__ = 'lra.allowance'

    salary_code = fields.Char('Salary Code', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    account_no = fields.Integer('Account Number', states={
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
    employee_group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ], "Employee Group", states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state']
    )
    imbursement = fields.Selection([
        ('1', 'Membership fee of Professional Societies.'),
        ('2', 'Subscription of Scientific Journals.'),
        ('3', 'Purchase of books & journals.'),
        ('4', 'Equipments used for research purpose such as Desktop, Laptops, additional portable Hard Disks, Pen Drive, CDs & other computer peripherals.'),
        ('5', 'Repair/replacement expenses of such equipments. '),
        ('6', 'Photography equipments like photography Camera, lenses and their peripherals.'),
        ('7', 'Smart Phones with e-mail features.'),
        ('8', 'Transparencies, slides and similar resources material required to enhance the learning.'),
        ],'Imbursement', states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('submit', 'Submit'),
            ('account_officer', 'Account Officer'),
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
                    ['account_officer'
                     ]),
            },


            "approve": {
                'invisible': ~Eval('state').in_(
                    ['account_officer'
                     ]),
                
            },
            
        })
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('confirm', 'submit'),
            ('submit', 'account_officer'),
            ('account_officer', 'approve'),
            ('account_officer', 'cancel'),
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
    @Workflow.transition('account_officer')
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
