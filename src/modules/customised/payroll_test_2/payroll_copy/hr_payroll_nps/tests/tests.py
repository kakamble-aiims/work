# This file is part of Tryton.  The COPYRIGHT file at the top level of

# this repository contains the full copyright notices and license terms.

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HrpayrollnpsTestCase(ModuleTestCase):

    'Test Hr Payroll NPS module'

    module = 'hr_payroll_nps'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HrpayrollnpsTestCase))
    return suite
