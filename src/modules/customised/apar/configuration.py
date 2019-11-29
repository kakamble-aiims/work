from datetime import datetime
from trytond.model import (ModelSQL, ModelView, ModelSingleton, fields)
from trytond.pool import Pool


__all__ = ['AparTemplateConfiguration']


class AparTemplateConfiguration(ModelSingleton, ModelSQL, ModelView):
    'Apar Template Configuration'

    __name__ = 'apar.form.template.configuration'

    start_date_apar = fields.Date('Start Date of APAR', required=True)
    last_date_emp_fill = fields.Date('Last Date to Fill APAR by Employee', required=True)
    last_date_reporting = fields.Date('Last Date for Reporting Officer', required=True)
    last_date_reviewing = fields.Date('Last Date for Reviewing Officer', required=True)
    last_date_accepting = fields.Date('Last Date for Accepting Authority', required=True)
    last_date_emp_sign = fields.Date('Last Date to Sign APAR by Employee', required=True)
    last_date_emp_represent = fields.Date('Last Date to Raise Representation by Employee', required=True)

    @staticmethod
    def _get_execution_user():
        return Pool().get('ir.model.data').get_id(
            'apar', 'user_managing_crons')

    @staticmethod
    def _get_request_user():
        # TODO: Find a better solution to get the user from apar technical admin 
        return Pool().get('ir.model.data').get_id(
            'res', 'user_admin')

    @classmethod
    def create_cron(cls, date, field):
        pool = Pool()
        Cron = pool.get('ir.cron')
        Field = pool.get('ir.model.field')
        desc = Field.search([('name', '=', field)])[0].field_description
        Cron.create([{
            "name": "APAR " + desc,
            "user": cls._get_execution_user(),
            "interval_number": 12,
            "interval_type": 'months',
            "request_user": cls._get_request_user(),
            "next_call": datetime.combine(date, datetime.max.time()),
            "model": 'apar.employee.form',
            "function": "cron_" + field,
        }])

    @classmethod
    def create(cls, vals):
        val = vals[0]
        for key in val:
            if key not in ('start_date_apar', 'last_date_emp_represent'):
                cls.create_cron(val.get(key), key)
        return super().create(vals)

    @classmethod
    def write(cls, records, vals):
        '''Override write method to change the cron job times'''
        print (vals)
        return super().write(records, vals)