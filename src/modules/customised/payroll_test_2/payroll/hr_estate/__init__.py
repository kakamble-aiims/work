from trytond.pool import Pool
from .hr_estate import *
from .estate_report import *


def register():
    Pool.register(
        EstateAllotment,
        QuarterType,
        QuarterTypeLocation,
        LicenseFeeSchedule,
        module='hr_estate', type_="model")
    Pool.register(
        LicenseFeeScheduleWiz,
        module='hr_estate', type_='wizard')
    Pool.register(
        LicenseFeeReport,
        module='hr_estate', type_='report')
