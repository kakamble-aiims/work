cd workspace/tryton/tryton50/src/modules/customised/payroll/gpf
source ../../../../../bin/activate
python setup.py install
trytond-admin -c ../../../../trytond.conf -v -d payroll_15july -u gpf
trytond -c ../../../../trytond.conf -v