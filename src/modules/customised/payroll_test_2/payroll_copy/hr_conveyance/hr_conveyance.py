from trytond.model import ModelSQL, ModelView, fields
from trytond.pyson import Eval, Bool
from trytond.model import Workflow
from trytond.pool import Pool
from trytond.transaction import Transaction


_all_ = [
    'Conveyance_Allowance',
]


class Conveyance_Allowance(Workflow, ModelSQL, ModelView):
    """Employee Conveyance Allowance"""

    __name__ = 'employee_conveyance.allowance'

    salary_code = fields.Char('Salary Code',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    employee = fields.Many2One('company.employee', 'Employee Name',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    designation = fields.Many2One('company.employee','Designation')
    department = fields.Many2One('company.employee','Department')
    transport_amount = fields.Float('Transport Amount',
        states={
            'readonly': ~Eval('state').in_(['draft']),
        }, depends=['state'])
    # vehicle = fields.Selection(
    #     [
    #         ('yes','Yes'),
    #         ('no','No')
    #     ], 'Do you have own vehicle')
    # transport = fields.Boolean('Transport') 

    # vehicle_selection = fields.Selection(
    #     [
    #         ('motor_car', 'Motor Car'),
    #         ('non_vehicle', 'Non Vehicle'),
    #         ('scooter', 'Scooter')
    #     ], 'Select Type Of Vehicle', states={
    #         'invisible': ~Bool(Eval('vehicle')),
    #         'required': ~Bool(Eval('vehicle')),
    #     }, depends=['vehicle'])
    
    # vehicle_regno = fields.Char('Vehicle Registration No.')
    # distance = fields.Selection(
    #     [
    #         ('1', '201-300 kilometers'),
    #         ('2', '301-450 kilometers '),
    #         ('3', '451-600 kilometers'),
    #         ('3', '601-800 kilometers'),
    #         ('3', 'Above 800 kilometers')
    #     ], 'Select Travel Distance')

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
            ('account_officer', 'Account Officer'),
            ('cancel', 'Cancel'),
            ('approve', 'Approve'),
            
        ], 'Status', readonly=True)

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls._buttons.update({
            "confirm": {
                'invisible': ~Eval('state').in_(
                    ['draft'
                     ]),
            },

            "submit": {
                'invisible': ~Eval('state').in_(
                    ['confirm'
                     ]),
            },


            "cancel": {
                'invisible': ~Eval('state').in_(
                    ['draft', 'account_officer'
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
            ('draft', 'cancel'),
            ('confirm', 'account_officer'),
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

    @fields.depends('employee')
    def on_change_employee(self):
        if self.employee:
            self.salary_code = self.employee.salary_code
            self.designation = self.employee.designation
            self.department = self.employee.department

    @staticmethod
    def default_employee():
        global current_employee
        current_employee = None
        pool = Pool()
        Employee = pool.get('company.employee')
        employee_id = Transaction().context.get('employee')
        employee = Employee.search([
            ('id', '=', employee_id)
        ])
        if employee != []:
            current_employee = employee[0]
        return current_employee.id if current_employee else None
    

    # @fields.depends('vehicle', 'vehicle_selection')
    # def on_change_vehicle(self):
    #     if self.vehicle != '1':
    #         self.vehicle_selection = ''

    