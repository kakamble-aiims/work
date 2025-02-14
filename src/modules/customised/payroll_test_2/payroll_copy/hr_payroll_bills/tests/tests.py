# This file is part of Tryton.  The COPYRIGHT file at the top level of

# this repository contains the full copyright notices and license terms.

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HrpayrollBillsTestCase(ModuleTestCase):

    'Test Hr Payroll Bills module'
    module = 'hr_payroll_bills'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HrpayrollBillsTestCase))
    return suite
