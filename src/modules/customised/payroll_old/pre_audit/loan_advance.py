from trytond.model import ModelSQL, ModelView, fields, Workflow
from trytond.pyson import Eval

__all__ = ['AdvanceApplication', 'ApplicationSignature']


class AdvanceApplication(Workflow, ModelSQL, ModelView):
    '''Advance Application'''

    __name__ = 'loan_advance.application'

    employee = fields.Many2One(
        'company.employee',
        'Employee',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        })
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('dealing', 'Dealing'),
        ('pre_audit', 'Pre Audit'),
        ('approved', 'Approved'),
        ('generate_sanction', 'Generate Sanction'),
        ('release', 'Release'),
        ('reject', 'Rejected')
    ], 'Status', readonly=True)
    type_of_advance = fields.Selection([
        ('hba', 'House Building Advance'),
        ('computer', 'Computer Loan')
        ],
        'Type of Advance',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        })
    anticipated_price = fields.Float(
        'Anticipated price',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        })
    amt_advance_reqd = fields.Float(
        'Amount of advance required',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        })
    no_of_instalments_desired = fields.Integer(
        'Number of instalments in which the advance is desired to be paid',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    advance_similar = fields.Boolean(
        'Whether advance for similar purpose was obtained previously?',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    similar_if_so_date_drawal = fields.Date(
        'Date of drawal of advance',
        states={
            'required': Eval('advance_similar') == '1',
            'invisible': Eval('advance_similar') != '1',
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['advance_similar']
    )
    amount_of_advance = fields.Float(
        'Amount of advance',
        states={
            'required': Eval('advance_similar') == '1',
            'invisible': Eval('advance_similar') != '1',
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['advance_similar']
    )
    interest_withstanding = fields.Float(
        'Interest thereon still outstanding if any',
        states={
            'invisible': Eval('advance_similar') != '1',
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['advance_similar']
    )
    intention_to_purchase_new_old_comp = fields.Boolean(
        'Intention to purchase a new or old personal computer',
        states={
            'invisible': ~Eval('type_of_advance').in_(['computer']),
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['type_of_advance']
    )
    purchase_through_reputed_agency = fields.Boolean(
        """If the intention is to purchase Personal Computer   
        through a regular or reputed dealer or agent, whether
        previous sanction of the Director has been obtained as
        required under Rule 18(3) of the Central Civil
        Services(Conduct) Rules 1964""",
        states={
            'invisible': ~Eval('type_of_advance').in_(['computer']),
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['type_of_advance']
    )
    whether_officer_leave = fields.Boolean(
        'Whether officer is on leave or about to proceed on leave?',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    leave_start_date = fields.Date(
        'Date of commencement of leave',
        states={
            'required': Eval('whether_officer_leave') == '1',
            'invisible': Eval('whether_officer_leave') != '1',
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['whether_officer_leave']
    )
    leave_end_date = fields.Date(
        'Date of expire of leave',
        states={
            'required': Eval('whether_officer_leave') == '1',
            'invisible': Eval('whether_officer_leave') != '1',
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['whether_officer_leave']
    )
    negotiations = fields.Boolean(
        """Are any negotiations or preliminary enquiry being made so that
        delivery may be taken of the Personal Computer within one month
        from the date of drawal of advance""",
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    certified_info_true = fields.Boolean(
        'Certified that the inofrmation given is complete and true',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    certified_purchase = fields.Boolean(
        """Certified that I have not taken delivery of the Peronal Computer 
        on account of which I apply for the advance that I shall complete 
        negotiations for the purchase of pay finally and taken possession of 
        the Personal Computer before the expiry of one month from the date of drawal
        of advance and that I shall insure it from the date of taking delivery of it""",
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }
    )
    signatures = fields.One2Many(
        'loan_advance.application_signature',
        'application',
        'Signatures'
    )

    @staticmethod
    def default_state():
        return 'draft'
    
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'confirm': {
                'invisible': ~Eval('state').in_(['draft'])
            },
            'send_to_dealing': {
                'invisible': ~Eval('state').in_(['confirm'])
            },
            'send_to_pre_audit': {
                'invisible': ~Eval('state').in_(['dealing'])
            },
            'approve': {
                'invisible': ~Eval('state').in_(['pre_audit'])
            },
            'generate_sanction_bill': {
                'invisible': ~Eval('state').in_(['approved'])
            },
            'release_loan': {
                'invisible': ~Eval('state').in_(['generate_sanction'])
            },
        })
        cls._transitions = set((
            ('draft', 'confirm'),
            ('confirm', 'dealing'),
            ('dealing', 'pre_audit'),
            ('pre_audit', 'approved'),
            ('approved', 'generate_sanction'),
            ('generate_sanction', 'release'),
        ))

    @classmethod
    @Workflow.transition('confirm')
    def confirm(cls):
        pass
    
    @classmethod
    @Workflow.transition('dealing')
    def send_to_dealing(cls):
        pass
    
    @classmethod
    @Workflow.transition('pre_audit')
    def send_to_pre_audit(cls):
        pass
    
    @classmethod
    @Workflow.transition('approved')
    def approve(cls):
        pass
    
    @classmethod
    @Workflow.transition('generate_sanction')
    def generate_sanction_bill(cls):
        pass
    
    @classmethod
    @Workflow.transition('release')
    def release_loan(cls):
        pass


class ApplicationSignature(ModelSQL, ModelView):
    '''Application Signature'''

    __name__ = 'loan_advance.application_signature'

    signed_by_user = fields.Many2One('res.user', 'Signed By')
    signed_by_employee = fields.Many2One(
        'company.employee',
        'Signed By Employee'
        )
    signed_on = fields.DateTime('Signed On')
    note = fields.Text('Remarks')
    designation = fields.Many2One(
        'employee.designation',
        'Designation'
        )
    place = fields.Char('Place')
    application = fields.Many2One(
        'loan_advance.application',
        'Application'
        )