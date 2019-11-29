from trytond.model import ModelSQL, ModelView, Workflow, fields
from trytond.pyson import Eval
from trytond.pool import Pool

__all__ = [
        'EstateAllotment', 'QuarterType',
        'QuarterTypeLocation']


class EstateAllotment(Workflow, ModelSQL, ModelView):
    """Employee Allotment"""

    __name__ = "estate.allotment"

    employee = fields.Many2One('company.employee', 'Employee', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    center = fields.Many2One(
        'gnuhealth.institution',
        'Center Name',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state'])
    department = fields.Many2One(
        'company.department',
        'Department',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state'])
    salary_code = fields.Char(
        'Salary Code',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state'])
    quarter_no = fields.Char('Quarter No.', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    location = fields.Selection(
        [
            ('ansari_nagar_east', 'Ansari Nagar(E)'),
            ('ansari_nagar_west', 'Ansari Nagar(W)'),
            ('masjid_moth', 'Masjid Moth'),
            ('a_v_nagar_old', 'Ayurvigyan Nagar(Old)'),
            ('a_v_nagar_new', 'Ayurvigyan Nagar(New)'),
            ('asiad_village_complex', 'Asiad Village Complex'),
            ('ballabhgarh', 'Ballabhgarh'),
        ], 'Location', states={
            'readonly': ~Eval('state').in_(['draft'])
        }, depends=['state'])
    quarter_type = fields.Many2One(
        'estate.quarter_type',
        'Quarter Type',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state', 'location'],
        domain=[
            ('locations', '=', Eval('location'))
        ])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('submit', 'Submit')
    ], 'Status', required=True, readonly=True)
    garage = fields.Boolean(
        'Garage?',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    servant_quarter = fields.Boolean(
        'Servant Quarter?',
        states={
            'readonly': ~Eval('state').in_(['draft'])
        },
        depends=['state'])
    date_of_allocation = fields.Date('Date of Allocation', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    date_of_occupation = fields.Date('Date of Occupation', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    date_of_vacation = fields.Date('Date of Vacation', states={
        'readonly': ~Eval('state').in_(['draft'])
    }, depends=['state'])
    license_fee = fields.Function(
        fields.Float('License Fee'),
        'get_license_fee'
    )
    water_charges = fields.Function(
        fields.Float('Water Charges'),
        'get_water_charges'
    )
    garage_fee = fields.Function(
        fields.Float('Garage'),
        'on_change_with_garage_fee'
    )
    servant_quarter_fee = fields.Function(
        fields.Float('Servant Quarter'),
        'on_change_with_servant_quarter_fee'
    )


    @staticmethod
    def default_state():
        return 'draft'

    @staticmethod
    def default_license_fee():
        return 0

    @staticmethod
    def default_water_charges():
        return 0

    @staticmethod
    def default_garage_fee():
        return 0

    @staticmethod
    def default_servant_quarter_fee():
        return 0

    @fields.depends('employee', 'center_name', 'department_name', 'salary_code')
    def on_change_employee(self):
        if self.employee:
            self.center = self.employee.center if self.employee.center else None
            self.department = self.employee.department if self.employee.department else None
            self.salary_code = self.employee.salary_code if self.employee.salary_code else ''
    
    def get_license_fee(self, name):
        if self.quarter_type:
            return self.quarter_type.license_fee
        else:
            return 0
        return self.quarter_type.license_fee    
    
    def get_water_charges(self, name):
        if self.quarter_type:
            return self.quarter_type.water_charges
        else:
            return 0
        return self.quarter_type.water_charges

    
    
    @fields.depends('garage')
    def on_change_with_garage_fee(self, name=None):
        # import pdb;pdb.set_trace()
        garage_fee = 0
        if self.garage:
            garage_fee = 40
        else:
            garage_fee = 0
        return garage_fee

    @fields.depends('servant_quarter')
    def on_change_with_servant_quarter_fee(self, name=None):
        servant_quarter_fee = 0
        if self.servant_quarter:
            servant_quarter_fee = 70
        else:
            servant_quarter_fee = 0
        return servant_quarter_fee  
    
    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._transitions |= set((
            ('draft', 'confirm')
            # ('confirm', 'submit')
        ))
        cls._buttons.update({
            'confirm_details': {
                'invisible': ~Eval('state').in_(['draft']),
                'depends': ['state']
            }
            # 'submit': {
            #     'invisible': ~Eval('state').in_(['confirm']),
            #     'depends': ['state']
            # }
        })

    @classmethod
    @Workflow.transition('confirm')
    def confirm_details(cls, records):
        pass

    # @classmethod
    # @Workflow.transition('submit')
    # def submit(cls, records):
    #     pass


class QuarterType(ModelSQL, ModelView):
    '''Quarter Type'''

    __name__ = "estate.quarter_type"

    name = fields.Char('Name')
    license_fee = fields.Float('License Fee')
    water_charges = fields.Float('Water Charges')
    locations = fields.One2Many(
        'estate.quarter_type_location',
        'quarter_type',
        'Locations'
    )


class QuarterTypeLocation(ModelSQL, ModelView):
    '''Quarter Type Location'''
    
    __name__ = 'estate.quarter_type_location'

    quarter_type = fields.Many2One('estate.quarter_type', 'Quarter Type')
    name = fields.Char('Location')
# class Quarter(ModelSQL, ModelView):
#     '''Quarter'''
#     name = fields.Char('Name')
#     quarter_type = fields.Char('Quarter Type')


# class OccupationReport(Report):
#     '''Occupation Report'''

#     __name__ = 'hr.estate.occupation_report'
