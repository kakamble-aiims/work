import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.pool import Pool
from trytond.tests.test_tryton import doctest_teardown
from trytond.tests.test_tryton import doctest_checker
from trytond.modules.company.tests import create_company


class HraTestCase(ModuleTestCase):

    'Test Hra module'
    module = 'hr_hra'

    @with_transaction()
    def test_employee_data(self):
        'Create employee'
        pool = Pool()
        party_cur = None
        company = create_company()
        Employee = pool.get('company.employee')
        party = pool.get('party.party')
        party = party.create([{
            'name': 'party ',
            }])
        if party != []:
            party_cur = party[0]
        employee = Employee.create([{
            'company': company,
            'party': party_cur,
            'employee_group': 'A',
            'employee_status': 'Regular',
            'primary_phone': '9935164850'
            }])
        if employee != []:
            employee_cur = employee[0]
        self.assertTrue(employee_cur.id)

    @with_transaction()
    def test_salary_code(self):
        'Test salary code constraint'
        pool = Pool()
        party_cur = None
        company = create_company()
        Employee = pool.get('company.employee')
        party = pool.get('party.party')
        party = party.create([{
            'name': 'party ',
            }])
        if party != []:
            party_cur = party[0]
        salary_code = None
        employee = Employee.create([{
            'company': company,
            'party': party_cur,
            'employee_group': 'A',
            'employee_status': 'Regular',
            'primary_phone': '9935164850'
            }])
        if employee != []:
            employee_cur = employee[0]
        salary_code = 5555

        self.assertRaises(Exception, Employee.write, [employee_cur], {
                'salary_code':  salary_code,
                })


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(HraTestCase))
    suite.addTests(doctest.DocFileSuite(
        'scenario_hra.rst',
        tearDown=doctest_teardown, encoding='utf-8',
        checker=doctest_checker,
        optionflags=doctest.REPORT_ONLY_FIRST_FAILURE))
    return suite
