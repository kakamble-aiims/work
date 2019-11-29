from datetime import datetime
from trytond.model import (ModelSQL, ModelView, Workflow, fields)
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
    Button
from trytond.pyson import Eval, PYSONEncoder
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction


__all__ = [
    'AparRepresentationForm', 'AparRepresentationSignatures',
    'APARGenerateRepRaiseWiz', 'APARGenerateRepShow',
    'IrModelField']


class AparRepresentationForm(Workflow, ModelSQL, ModelView):
    'APAR Representation Form'

    __name__ = 'apar.representation'

    mail = fields.Boolean('Mail')
    representation_id = fields.Char('Representation Number', readonly=True)
    raised_by = fields.Many2One('company.employee', 'Employee', readonly=True)
    subject = fields.Char(
        'Subject', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    text = fields.Text(
        'Details', states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'],)
    raised_on = fields.Date('Raised On', readonly=True)
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('reporting_officer', 'Reporting Officer'),
            ('reviewing_officer', 'Reviewing Officer'),
            ('hod', 'HOD'),
            ('accepting_authority','Accepting Authority'),
            ('acr_cell', 'ACR Cell'),
            ('submitted_to_acr_cell', 'Submitted to ACR Cell'),
            ('director', 'Director'),
            ('closed', 'Closed')
        ], 'Status', readonly=True
    )
    comments_reporting = fields.Text(
        'Comments by Reporting Officer', states={
            'readonly': ~Eval('state').in_(['reporting_officer']),
        }, depends=['state'],)
    comments_reviewing = fields.Text(
        'Comments by Reviewing Officer', states={
            'readonly': ~Eval('state').in_(['reviewing_officer']),
        }, depends=['state'],)
    comments_accepting = fields.Text(
        'Comments by Accepting Authority', states={
            'readonly': ~Eval('state').in_(['accepting_authority']),
        }, depends=['state'],)
    comments_hod = fields.Text('Comments by HoD', states={
            'readonly': ~Eval('state').in_(['hod']),
        }, depends=['state'],)
    comments_director = fields.Text(
        'Comments by Director', states={
            'readonly': ~Eval('state').in_(['director']),
        }, depends=['state'],)
    present_score = fields.Integer('Present Score')
    score = fields.Integer('Final Score')
    signatures = fields.One2Many(
        'apar.representation.signatures', 'representation', 'Signatures')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "submit": {
                'invisible': ~Eval('state').in_(
                    ['draft']),
                'depends': ['state']
            },
            "forward_to_reporting": {
                'invisible': ~Eval('state').in_(
                    ['submitted_to_acr_cell']),
                'depends': ['state']
            },
            "forward_to_reviewing": {
                'invisible': ~Eval('state').in_(
                    ['reporting_officer']),
                'depends': ['state']
            },
            "forward_to_accepting": {
                'invisible': ~Eval('state').in_(
                    ['reviewing_officer']),
                'depends': ['state']
            },
            "forward_to_HoD": {
                'invisible': ~Eval('state').in_(
                    ['accepting_authority']),
                'depends': ['state']
            },
            "forward_to_acr": {
                'invisible': ~Eval('state').in_(
                    ['hod']),
                'depends': ['state']
            },
            "forward_to_director": {
                'invisible': ~Eval('state').in_(
                    ['acr_cell']),
                'depends': ['state']
            },
            "close": {
                'invisible': ~Eval('state').in_(
                    ['director']),
                'depends': ['state']
            }
        })

        cls._transitions |= set((
            ('draft', 'submitted_to_acr_cell'),
            ('submitted_to_acr_cell', 'reporting_officer'),
            ('reporting_officer', 'reviewing_officer'),
            ('reviewing_officer', 'accepting_authority'),
            ('accepting_authority', 'hod'),
            ('hod', 'acr_cell'),
            ('acr_cell', 'director'),
            ('director', 'closed'),
            ('closed', 'closed'),
        ))

    @staticmethod
    def default_state():
        return 'draft'
    
    def form_signature(self):

        pool = Pool()
        sign_obj = pool.get('apar.representation.signatures')
        User = pool.get('res.user')
        user = User(Transaction().user)

        employee = user.employee
        place = 'Delhi'

        vals = {
            'signed_by_user': user.id,
            'signed_by_employee': employee.id if employee else None,
            'designation': employee.designation.id if employee else None,
            'signed_on': pool.get('ir.date').today(),
            'place': place,
            'representation': self.id
        }

        sign_obj.create([vals])

    @classmethod
    @ModelView.button
    @Workflow.transition('submitted_to_acr_cell')
    def submit(self, records):
        for record in records:
            record.form_signature()
    
    @classmethod
    @ModelView.button
    @Workflow.transition('reporting_officer')
    def forward_to_reporting(self, records):
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('reviewing_officer')
    def forward_to_reviewing(self, records):
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('accepting_authority')
    def forward_to_accepting(self, records):
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('hod')
    def forward_to_HoD(self, records):
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('acr_cell')
    def forward_to_acr(self, records):
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('director')
    def forward_to_director(self, records):
        # TODO: Confirm from the user
        #  if he is sure that he wants to sign the document.
        for record in records:
            record.form_signature()

    @classmethod
    @ModelView.button
    @Workflow.transition('closed')
    def close(self, records):
        for record in records:
            record.form_signature()


class AparRepresentationSignatures(ModelSQL, ModelView):
    'Apar Representation Signatures'

    __name__ = 'apar.representation.signatures'

    signed_by_user = fields.Many2One('res.user', 'Signed By', required=True)
    signed_by_employee = fields.Many2One(
        'company.employee', 'Signed By Employee')
    signed_on = fields.Date('Signed On', required=True)
    designation = fields.Many2One('employee.designation', 'Designation')
    place = fields.Char('Place')
    representation = fields.Many2One('apar.representation', 'Representation')


class APARGenerateRepShow(ModelView):
    'APAR Representation Show'
    __name__ = 'apar.representation.raise.show'

    subject = fields.Char('Subject')
    details = fields.Text('Details')
    representation = fields.Many2One(
        'apar.representation', 'Representation')


class APARGenerateRepRaiseWiz(Wizard):
    'APAR Representation Wizard'
    __name__ = 'apar.representation.raise'

    start_state = 'raises'
    raises = StateView(
        'apar.representation.raise.show',
        'apar.form_apar_representationshow_view',
        [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button(
                'Generate Representation',
                'create_repr',
                'tryton-go-next',
                default=True,
            )])
    create_repr = StateTransition()
    open_ = StateAction('apar.act_apar_representation')

    def create_representation(self):
        pool = Pool()
        context = Transaction().context
        repr_ = pool.get('apar.representation').create([{
            'raised_by': pool.get('res.user')(Transaction().user).employee,
            'subject': self.raises.subject,
            'text': self.raises.details,
            'raised_on': pool.get('ir.date').today()
        }])[0]
        self.raises.representation = repr_
        EmployeeForm = pool.get('apar.employee.form')
        active_rec = EmployeeForm(context.get('active_id'))
        pool.get('apar.employee.form').set_representation([active_rec])
        active_rec.representation = repr_
        active_rec.save()
    
    def transition_create_repr(self):
        self.create_representation()
        return 'open_'

    def do_open_(self, action):
        action['pyson_domain'] = PYSONEncoder().encode([
            ('id', '=', self.raises.representation.id)])
        return action, {}


class IrModelField(metaclass=PoolMeta):
    "Model Field"

    __name__ = "ir.model.field"

    @classmethod
    def search(cls, domain, offset=0, limit=None, order=None, count=False):
        '''Overriding Search'''
        for n, expr in enumerate(domain):
            if expr[0] == 'model' and isinstance(expr[2], str):
                Model = Pool().get('ir.model')
                model = Model.search([('model', '=', expr[2])], limit=1)
                if model:
                    model = model[0].id
                    domain[n] = (expr[0], expr[1], model)
        return super().search(domain, offset, limit, order, count)
