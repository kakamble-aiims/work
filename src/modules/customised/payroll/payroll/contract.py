from trytond.model import ModelSQL, ModelView, fields
from trytond.pool import Pool, PoolMeta

__all__ = ['Contract']


class Contract(metaclass=PoolMeta):

    __name__ = 'hr.contract'

    structure = fields.Many2One('salary.structure', 'Salary Structure')
