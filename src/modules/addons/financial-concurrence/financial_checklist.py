from datetime import datetime
from trytond.model import (ModelSQL, ModelView, fields, Workflow)
from trytond.wizard import Wizard, StateTransition, StateView, StateAction, \
     Button
from trytond.pyson import Eval, Bool, PYSONEncoder, If, Or, Not, And
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta

__all__ = [
           'AccountConcurrenceChecklist',
           'AccountConcurrenceChecklistLine',
           'FinancialConcurrenceStage',
           'AccountConcurrenceChecklistLineItem',
         ]


class AccountConcurrenceChecklist(Workflow, ModelSQL, ModelView):
    '''Account Concurrence Checklist'''

    __name__ = 'account.concurrence.checklist'

    raised_by = fields.Many2One('company.employee', 'Raised By')
    raised_on = fields.DateTime('Raised On')
    file_number = fields.Char('File number')
    name = fields.Char('Name')
    e_office_file_number = fields.Char('E-Office file number')
    department = fields.Many2One('company.department', 'Department')
    line = fields.One2Many('account.concurrence.checklist.line',
                           'checklist', 'Line')
    state = fields.Selection(
        [
            ('draft', 'draft'),
            ('confirm', 'confirm'),
            ('submit', 'Submit'),
            ('cancel', 'Cancel'),
            ('reject', 'Reject'),
            ('approved', 'Approved'),
        ], 'State', sort=False)

    @staticmethod
    def default_state():
        ''' return Default-draft state.'''
        return 'draft'
        pass

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'confirm': {
                'invisible': ~Eval('state').in_(['draft']),
                'depends': ['state']
            },
            'cancel': {
                'invisible': ~Eval('state').in_(['draft', 'confirm']),
                'depends': ['state']
            },
            'submit': {
                'invisible': ~Eval('state').in_(['confirm']),
                'depends': ['state']
            },
            'reject': {
                'invisible': ~Eval('state').in_(['submit']),
                'depends': ['state']
            },
            'approve': {
                'invisible': ~Eval('state').in_(['submit']),
                'depends': ['state']
            },
            })
        cls._transitions |= set((
            ('draft', 'confirm'),
            ('draft', 'cancel'),
            ('confirm', 'cancel'),
            ('confirm', 'submit'),
            ('submit', 'reject'),
            ('submit', 'approved')
        ))

    @classmethod
    @ModelView.button
    @Workflow.transition('confirm')
    def confirm(cls, records):
        ''' Button to cancel the checklist. '''
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('cancel')
    def cancel(cls, records):
        ''' Button to cancel the checklist. '''
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('submit')
    def submit(cls, records):
        ''' Button to submit the checklist. '''
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('reject')
    def reject(cls, records):
        ''' Button to reject the checklist. '''
        pass

    @classmethod
    @ModelView.button
    @Workflow.transition('approved')
    def approve(cls, records):
        ''' Button to approved the checklist. '''
        pass


class AccountConcurrenceChecklistLine(Workflow, ModelSQL, ModelView):
    '''Account Concurrence Checklist Line'''

    __name__ = 'account.concurrence.checklist.line'
    stage = fields.Many2One('financial.concurrence.stage', 'Stage')
    section = fields.Char('Section')
    particulars = fields.Many2One('account.concurrence.checklist.line.item',
                                  'Particulars',
                                   domain = [('stage', "=", Eval('stage'))]
                                  )
    comments = fields.Selection(
        [
            ('yes', 'Yes'),
            ('no', 'No'),
            ('not_applicable', "Not Applicable")
        ], 'Comments', sort=False)

    remarks = fields.Char('Remarks')
    page_number = fields.Integer('Page Number',)
    checklist = fields.Many2One('account.concurrence.checklist.line.item',
                                'Checklist')

    # @classmethod
    # def default_record(cls):
    #     vals = []
    #     line = Pool().get('account.concurrence.checklist')
    #     lines = line.search([])
    #     for line in lines:
    #         vals.append({
    #             'line': line.id,
    #             'stage': stage.id,
    #             'section': section.id,
    #             'particulars':particulars.id,
    #             'checklist': line.checklist.id if line.checklist else None,
    #         })
    #     return vals


class FinancialConcurrenceStage(ModelSQL, ModelView):
    '''Financial Concurrence Stage'''

    __name__ = 'financial.concurrence.stage'
    name = fields.Char('Stage')


class AccountConcurrenceChecklistLineItem(ModelSQL, ModelView):
    '''Account Concurrence Checklist Line Item'''

    __name__ = 'account.concurrence.checklist.line.item'
    name = fields.Char('Particulars')
    stage = fields.Many2One('financial.concurrence.stage', 'Stage')
