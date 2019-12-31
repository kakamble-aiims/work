from trytond.pool import Pool
from .hr_ota import *
from .ota_report import *


def register():
    Pool.register(
        OverTimeAllowance,
        OtaEmployeeList,
        OtEmployee,
        OtaList,
        OTASchedule,
        module='hr_ota', type_='model')

    Pool.register(
        OverTimeAllowanceWiz,
        OTAScheduleWiz,
        module='hr_ota', type_='wizard')
    Pool.register(
        OTAReport,
        module='hr_ota', type_='report')
