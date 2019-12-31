from trytond.pool import Pool
from .schedule import *


def register():
    Pool.register(
        OASchedule,
        EHSSchedule,
        module='hr_schedule', type_='model')
    Pool.register(
        OAScheduleWiz,
        EHSScheduleWiz,
        module='hr_schedule', type_='wizard')
    Pool.register(
        OAReport,
        EHSReport,
        module='hr_schedule', type_='report')
