# Health Extension for AIIMS

from trytond.model import ModelView, ModelSQL, fields, tree
from trytond.pool import PoolMeta

__all__ = ['Department', 'Establishment']


class Department(metaclass=PoolMeta):
    "AIIMS Departments"

    __name__ = "company.department"

    type_ = fields.Selection(
        [
            ('Medical', 'Medical'),
            ('Non-Medical', 'Non-Medical')
        ], "Type"
    )
    specialty = fields.Many2One(
        'gnuhealth.specialty', "Specialty",
        # TODO - If the type is medical, then this should be mandatory else
        # invisible
    )
    establishment = fields.Many2One('health.establishment', 'Establishment')
    institution = fields.Many2One(
        'gnuhealth.institution', 'Center', required=True,
        help='Health Center'
    )


class Establishment(ModelSQL, ModelView):
    "AIIMS Establishments"

    __name__ = "health.establishment"

    name = fields.Char('Establishment Name', required=True)
    center = fields.Many2One(
        'gnuhealth.institution', 'Center', required=True,
        help='Health Center'
    )
    admin = fields.Many2One(
        'company.employee', 'Admin',
        help='Administrator associated to this establishment.'
    )
    departments = fields.One2Many(
        'company.department', 'establishment', 'Departments'
    )
