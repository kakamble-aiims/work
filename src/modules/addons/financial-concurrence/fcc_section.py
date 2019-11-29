import csv

path = '/home/monika/Documents'
file_name = "fcc_section"

xml_rec = """<record id="fcc_section_{id}" model="account.concurrence.checklist.line.item">
    <field name="section">{name}</field>
</record>
"""
res = open('{path}/{file}.xml'.format(
        path=path,
        file=file_name
    ), 'w')
with open('{path}/{file}.csv'.format(
        path=path,
        file=file_name
                                    ), 'r') as data_file:
        data = csv.reader(data_file)
        for line in data:
            res.write(xml_rec.format(
                        id=line[0],
                        name=line[1],
                        ))