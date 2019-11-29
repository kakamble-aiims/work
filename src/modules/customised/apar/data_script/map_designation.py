import csv
import proteus
from datetime import datetime

path = '/home/monika/work/APAR/data'
file_name = "designation"

proteus_config = proteus.config.set_trytond(
    database='apar',
    user='admin',
    config_file='/home/monika/workspace/tryton/tryton50/src/trytond.conf'
)

# Get Models
Model = proteus.Model
Designation = Model.get('employee.designation')
Template = Model.get('apar.form.template')

templates = {}

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
    
        template_code = line[2]
        template_rec = templates.get(template_code, None)
        if not template_rec:
            template_rec = Template.find([('form_number', '=', template_code)])[0]
            templates[template_code] = template_rec
        
        print ("Searching designation = %s" % line[0])
        designation = Designation.find([('name', '=', line[0])])[0]
        designation.template = template_rec
        designation.save()

