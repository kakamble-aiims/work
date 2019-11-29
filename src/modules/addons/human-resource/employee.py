from trytond.model import (ModelSQL, ModelView, fields, tree)
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Not, Bool


__all__ = [
    'Party', 'Department', 'HrEmployee',
    'EmployeeDesignation', 'CompanyEmployeeGrade',
    'EmployeePosting', 'GradePay', 'Bank',
    'Leave', 'BankAccounts',
    'EmployeeDependents'
]


class Party(metaclass=PoolMeta):
    "Party Extension"

    __name__ = 'party.party'

    is_employee = fields.Boolean('Employee')
    appellation = fields.Selection(
        [
            (None, ''),
            ('Dr', 'Dr'),
            ('Mr', 'Mr'),
            ('Ms', 'Ms'),
            ('Mrs', 'Mrs')
        ], 'Appellation',
        states={'invisible': Not(Bool(Eval('is_employee')))}
    )


class Department(tree(separator=' / '), ModelView, ModelSQL):
    "Departments"

    __name__ = "company.department"

    name = fields.Char(
        'Department Name', required=True, translate=True,
    )
    code = fields.Char(
        'Code', required=True)
    parent = fields.Many2One(
        'company.department', 'Parent Department'
    )
    childs = fields.One2Many(
        "company.department", "parent", "Sub-Departments",
        readonly=True)

    note = fields.Text('Note')
    head = fields.Many2One('company.employee', 'Head of Department')
    employees = fields.One2Many('company.employee', 'department', 'Employees')
    postings = fields.One2Many('employee.posting', 'department', 'Postings')

    # TODO Order by name - Alphabetically Ascending


class HrEmployee(metaclass=PoolMeta):
    'HR Employee'

    __name__ = 'company.employee'

    party = fields.Many2One(
        'party.party', 'Employee', required=True,
        domain=[
            ('is_employee', '=', True),
            ('is_person', '=', True),
            ],
        help="The associated party record which represents the employee.")

    employee_id = fields.Char("Employee Code")
    salary_code = fields.Char("Salary Code")
    ehs = fields.Char("EHS Number")
    department = fields.Many2One("company.department", "Department")
    center = fields.Many2One('gnuhealth.institution', 'Center')
    designation = fields.Many2One("employee.designation", "Designation")
    primary_phone = fields.Char("Phone No.")
    primary_email = fields.Char("Email Address")
    date_of_joining = fields.Date('Date of Joining')


    # date_of_release
    employee_status = fields.Selection([
        ('Regular', 'Regular'),
        ('Adhoc', 'Adhoc'),
        ('Contractual', 'Contractual'),
        ('Deputation', 'Deputation'),
        ('Resigned', 'Resigned'),
        ('Retired', 'Retired')
    ], "Employee Status")
    employee_group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ], "Employee Group"
    )
    category = fields.Selection(
        [
            (None, ''),
            ('general', 'General'),
            ('sc', 'Scheduled Caste'),
            ('st', 'Scheduled Tribe'),
            ('obc', 'Other Backward Classes'),
            ('ph', 'Physically Handicapped')
        ], 'Category'
    )
    grade = fields.Many2One('company.employee.grade', 'Pay Matrix Level')
    pay_in_band = fields.Char('Pay in the Pay Band')
    grade_pay = fields.Many2One('company.employee.grade_pay', 'Grade Pay')
    is_eligible_for_hometown = fields.Boolean("If Eligible for Hometown")
    is_ehs_availed = fields.Boolean("If EHS Availed")
    is_exservicemen = fields.Boolean("If Ex-Servicemen")
    
    father_name = fields.Char("Father's Name")
    mother_name = fields.Char("Mother's Name")
    spouse_name = fields.Char("Spouse's Name")
    pan_number = fields.Char("PAN No.")
    driving_licence_number = fields.Char("Driving Licence No.")
    identification_mark = fields.Char("Identification Mark")
    height = fields.Char("Height")
    blood_group = fields.Selection(
        [
            ('', ''),
            ('A+', 'A+'),
            ('A-', 'A-'),
            ('B+', 'B+'),
            ('B-', 'B-'),
            ('AB+', 'AB+'),
            ('AB-', 'AB-'),
            ('O+', 'O+'),
            ('O-', 'O-'),
        ], "Blood Group")

    marital = fields.Selection(
        [
            (None, ''),
            ('single', 'Single'),
            ('married', 'Married'),
            ('widower', 'Widower'),
            ('divorced', 'Divorced')
        ], 'Marital Status')
    
    postings = fields.One2Many('employee.posting', "employee", 'Postings')
    education_qualification = fields.Text('Educational Qualification')
    date_of_resignation = fields.Date("Date of Resignation", states={
        'required': Eval('employee_status') == 'Resigned' 
    }, depends=['employee_status'])
    date_of_retirement = fields.Date("Date of Retirement", states={
        'required': Eval('employee_status') == 'Retired' 
    }, depends=['employee_status'])
    date_of_last_promotion = fields.Date("Date of Last Promotion")
    personal_file_no = fields.Char("Personal File No.")
    permission_file_no = fields.Char("Permission File No.")
    gpf_num = fields.Char("GPF No.")
    pran_num = fields.Char("PRAN No.")
    gpf_nominee = fields.Char("GPF Nominee")
    bank_accounts = fields.One2Many("bank.accounts", "employee", "Bank Accounts")


class EmployeePosting(ModelSQL, ModelView):
    "Employee Postings"

    __name__ = "employee.posting"

    employee = fields.Many2One("company.employee", "Employee", required=True)
    date_from = fields.Date("Date From", required=True)
    date_to = fields.Date("Date To")
    designation = fields.Many2One("employee.designation", "Designation", required=True)
    department = fields.Many2One("company.department", "Department", required=True)
    reporting_officer = fields.Many2One("company.employee", "Reporting Officer")


class EmployeeDesignation(ModelView, ModelSQL):
    "Employee Designation"

    __name__ = "employee.designation"

    name = fields.Char("Name")
    group = fields.Selection(
        [
            ('A', 'A'),
            ('B', 'B'),
            ('C', 'C'),
            ('D', 'D'),
        ], "Employee Group"
    )


class CompanyEmployeeGrade(ModelSQL, ModelView):
    "Employee Grade"

    __name__ = "company.employee.grade"

    name = fields.Char('Grade')


class GradePay(ModelSQL, ModelView):
    'Grade Pay'

    __name__ = "company.employee.grade_pay"

    name = fields.Char('Name')


class Leave(ModelSQL, ModelView):
    '''Leave'''

    __name__ = "company.employee.leave"

    employee = fields.Many2One("company.employee", "Employee")
    type_of_leave = fields.Selection(
        [
            ('Earned Leave', 'Earned Leave'),
            ('Half Pay Leave', 'Half Pay Leave'),
            ('Commuted Leave', 'Commuted Leave'),
            ('Leave Not Due', 'Leave Not Due'),
            ('Extraordinary Leave', 'Extraordinary Leave'),
            ('Maternity Leave', 'Maternity Leave'),
            ('Paternity Leave', 'Paternity Leave'),
            ('Leave on adoption of child', 'Leave on adoption of child'),
            ('Child Care Leave', 'Child Care Leave'),
            ('WRIIL', 'Work Related Illness and Injury Leave'),
            ('Sp. L SH', 'Special Leave connected with inquiry on sexual harrassment'),
            ('Study Leave', 'Study Leave'),
            ('Casual Leave', 'Casual Leave'),
            ('Special Casual Leave', 'Special Casual Leave'),
        ], "Type of Leave"
    )
    from_date = fields.Date("From Date")
    to_date = fields.Date("To Date")
    remarks = fields.Char("Remarks")


class BankAccounts(ModelSQL, ModelView):
    '''Bank Account'''

    __name__ = 'bank.accounts'

    name = fields.Char("Account Number", required=True)
    branch = fields.Char("Bank Branch")
    ifsc_code = fields.Char("IFSC Code", required=True)
    employee = fields.Many2One("company.employee", "Employee", required=True)
    bank = fields.Many2One("bank.bank", "Bank", required=True)


class EmployeeDependents(ModelSQL, ModelView):
    """Employee Dependents"""

    __name__ = 'company.employee.dependents'

    name = fields.Char("Name", required=True)
    employee = fields.Many2One("company.employee", "Employee")
    date_of_birth = fields.Date("Date of Birth")
    relationship = fields.Selection(
        [
            ('', ''),
            ('son', 'Son'),
            ('daughter', 'Daughter'),
            ('wife', 'Wife'),
            ('mother', 'Mother'),
            ('father', 'Father'),
            ('husband', 'Husband'),
            ('brother', 'Brother'),
            ('sister', 'Sister'),
            ('others', 'Others')
        ], "Relationship")
    mobile = fields.Char("Contact No.")


class Bank(ModelSQL, ModelView):
    '''Bank'''

    __name__ = "bank.bank"

    name = fields.Char("Name", required=True)
