# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .hr_gpf_change import *
from .hr_gpf_advance import *
from .hr_gpf_lines import *
from .gpf_report import *


def register():
    Pool.register(
        GPFSubscription,
        HrContract,
        HrEmployee,
        GPFAdvance,
        GPFreason,
        GPFCancelreason,
        GPFAdvanceLine,
        GPFLines,
        GPFSchedule,
        module='hr_gpf', type_='model')
    Pool.register(
        GPFScheduleWiz,
        module='hr_gpf', type_='wizard')
    Pool.register(
        GPFReport,
        module='hr_gpf', type_='report')
