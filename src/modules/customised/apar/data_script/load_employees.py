import csv
import proteus
from datetime import datetime

APPOINTMENT = [
    ('', 'Regular'),
    ('direct', 'Regular'),
    ('adhoc', 'Adhoc'),
    ('Contractual', 'Contractual'),
    ('on deputation', 'Deputation')
]

CATEGORY = [
    ('GENERAL', 'general'),
    ('SC', 'sc'),
    ('ST', 'st'),
    ('OBC', 'obc'),
    ('OTHER', 'ph')
]

file_names = [
    # "cder",
    # "cnc",
    'ctc',
    'estab',
    "faculty",
    "irch",
    "jpnatc",
    'main_do',
    "nddtc",
    "rpc",
]

path = '/home/prakhar/work/APAR/Data'
file_name = "faculty"

proteus_config = proteus.config.set_trytond(
    database='apar4',
    user='admin',
    config_file='/home/monika/workspace/tryton/tryton50/src/trytond.conf'
)

# Get Models
Model = proteus.Model
Party = Model.get('party.party')
User = Model.get('res.user')
PartyContact = Model.get('party.contact_mechanism')
Employee = Model.get('company.employee')
Designation = Model.get('employee.designation')
Center = Model.get('gnuhealth.institution')
Department = Model.get('company.department')
PayMatrixLevel = Model.get('company.employee.grade')
GradePay = Model.get('company.employee.grade_pay')
Posting = Model.get('employee.posting')
User = Model.get('res.user')

with open('{path}/{file}.csv'.format(
        path=path,
        file=file_name
    ), 'r') as data_file:
    data = csv.reader(data_file)
    count = 0
    for line in data:
        count += 1
        if count == 1:
            continue

        center_name = line[0]
        department_name = line[2] or line[1]
        ehs = line[3]
        employee_code = line[4]
        appellation = line[5]
        name = line[6].strip()
        gender = line[7].strip()
        father_name = line[8].strip()
        dob = line[9].strip()
        nationality = line[10].strip()
        category = line[12]
        date_of_joining = line[14]
        email = line[16].strip()
        mobile = line[17].strip()
        designation_name = line[18].strip()
        type_appoint = line[19].strip().lower()
        desig_join_date = line[21]
        pay_matrix_level = line[22]
        grade_pay = line[23]
        group = line[25].strip()

        if group != 'A':
            continue
        print (name)
            
        party = Party()

        party.is_person = True
        party.name = name


        # Map Gender
        if gender == 'Male':
            party.gender = 'm'
        elif gender == 'Female':
            party.gender = 'f'
        
        # Map DOB
        party.dob = datetime.strptime(dob, '%d/%m/%Y')

        party.is_employee = True
        party.appellation = appellation
        
        party.save()
        party_contact_mobile = PartyContact()
        party_contact_mobile.type = 'mobile'
        party_contact_mobile.value = mobile
        party_contact_mobile.party = party
        party_contact_mobile.save()

        party_contact_email = PartyContact()
        party_contact_email.type = 'email'
        party_contact_email.value = email
        party_contact_email.party = party
        party_contact_email.save()

        # Create Employees
        employee = Employee()
        employee.party = party

        print (center_name)

        # Search and map Center
        center = Center.find([
            'OR', 
                ('name.name', '=', center_name),
                ('code', '=', center_name)

        ])[0]

        # Search and map Department
        department = Department.find([
            ('name', '=', department_name),
            ('institution', '=', center)
        ])[0]

        employee.center = center
        employee.department = department
        employee.employee_id = employee_code


        # Search and Map Designation
        designation = Designation.find([('name', '=', designation_name)])
        if not designation:
            print ("{d} not found for {e}".format(d=designation_name, e=name))
        if len(designation) > 1:
            print ("More than 1 designation {d} found for {e}".format(d=designation_name, e=name))
        employee.designation = designation[0]
        employee.date_of_joining = datetime.strptime(date_of_joining, '%d/%m/%Y')

        # Map Type of Employement 
        employee.employee_status = dict(APPOINTMENT).get(type_appoint, 'Regular')
        employee.employee_group = group

        if pay_matrix_level:
            pay_matrix_level_ = PayMatrixLevel.find([('name', '=', pay_matrix_level)])
            if pay_matrix_level_:
                employee.grade = pay_matrix_level_[0]

        if grade_pay:
            grade_pay_ = GradePay.find([('name', '=', grade_pay)])
            if grade_pay_:
                employee.grade_pay = grade_pay_[0]
            else:
                grade_pay_new = GradePay()
                grade_pay_new.name = grade_pay
                grade_pay_new.save()
                employee.grade_pay = grade_pay_new


        employee.ehs = ehs
        employee.category = dict(CATEGORY).get(category)
        employee.primary_phone = mobile
        employee.primary_email = email
        employee.father_name = father_name
        employee.marital_status = None

        employee.save()

        posting = Posting()
        posting.employee = employee
        posting.date_from = datetime.strptime(desig_join_date, '%d/%m/%Y')
        posting.designation = designation[0]
        posting.department = department

        posting.save()

        if not mobile:
            print ("Missing Mobile: User not created for employee: {emp}".format(emp=name))
        else:
            user = User()
            user.login = mobile
            user.name = name
            user.email = email
            user.employees.append(employee)
            user.employee = employee
            try:
                user.save()
            except Exception:
                print ("User not created for employee: {employee}".format(employee=name))
