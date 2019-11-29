import requests
import json
from trytond.model import Workflow
from trytond.model import (ModelSQL, ModelView, fields)
from trytond.pyson import Eval, Bool, PYSONEncoder, If, Or, Not, And
import datetime
from trytond.model import Workflow
from trytond.pool import Pool, PoolMeta
from trytond.transaction import Transaction

__all__ = ['BankDetails', 'HrEmployee']

class BankDetails(ModelSQL, ModelView):
    '''Banks'''

    __name__ = 'res.bank'
    _rec_name = 'bank'

    bank = fields.Char('Bank Name')


class HrEmployee(metaclass=PoolMeta):
    '''Bank Details in HREmployee'''

    __name__ = 'company.employee'

    bank_name = fields.Many2One('res.bank', 'Bank Name')
    ifsc = fields.Char('IFSC Code',
                        help="Enter your IFSC code")
    bank_address = fields.Text('Bank Address', size=16)
    account_no = fields.Char('Account Number')
    bank_status = fields.Selection(
        [
            ('verified', 'Verified'),
            ('non_verified', 'Not Verified'),
            (None, '')
        ], 'Bank Account Status')

    end_point = "https://ifsc.razorpay.com/"

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            'verify_ifsc_button': {},
            'verify_account_number': {},
        })
    
    @classmethod
    def verify_ifsc_button(cls, records):
        '''To generate bank address'''

        for record in records:
            ifsc = record.ifsc
            uri = record.end_point + ifsc
            response = requests.get(uri)
            res_dict = response.json()
            if res_dict != 'Not Found':
                cls.write(records,
                    {'bank_address': res_dict['ADDRESS']}
                    )
            else:
                cls.raise_user_error('Please Enter Valid IFSC Number')

    @classmethod
    def verify_account_number(cls, records):
        '''to verify account number with PFMS'''
        pass

    @classmethod
    def validate(cls, records):
        super(HrEmployee, cls).validate(records)
        for record in records:
            if record.account_no:
                test_account_number=record.account_no.isdigit()
                if not test_account_number:
                    cls.raise_user_error('Enter Valid Account Number')
                if len(record.account_no)<9:
                    cls.raise_user_error('Enter Valid Account Number')
