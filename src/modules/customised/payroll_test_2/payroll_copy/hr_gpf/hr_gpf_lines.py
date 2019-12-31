from trytond.model import ModelSQL, ModelView, fields
import datetime
from trytond.pyson import Eval
from trytond.pool import Pool, PoolMeta
from trytond.model import Workflow
from trytond.transaction import Transaction

__all__ = [
    'GPFLines',
]


class GPFLines(Workflow, ModelSQL, ModelView):
    'GPF Lines'

    __name__ = 'hr.gpf.lines'

    amount = fields.Float('Amount')
    date = fields.Date('Date')
    description = fields.Char('Description')
    gpf_type = fields.Selection([
        ('interest', 'Interest'),
        ('deposit_subscribe', 'Deposit Subscribe'),
        ('deposit_loan', 'Deposit loan'),
        ('advance', 'Advance'),
        ('withdraw', 'Withdraw'),
        ('opening', 'Opening'),
    ], 'Type')
    gpf_lines = fields.Many2One('company.employee', 'GpfLines')

    
