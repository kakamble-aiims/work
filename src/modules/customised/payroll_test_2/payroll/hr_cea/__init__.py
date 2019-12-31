from trytond.pool import Pool
from .hr_cea import *
from .cea_report import *


def register():
    Pool.register(
        ChildernEductionAllowance,
        ChildrenEmployeeList,
        ChildrenEmployee,
        ChildrenList,
        TutionFeeSchedule,
        module='hr_cea', type_='model')
    Pool.register(
        ChildrenEduactionAllowanceWiz,
        TutionFeeScheduleWiz,
        module='hr_cea', type_='wizard')
    Pool.register(
        TutionFeeReport,
        module='hr_cea', type_='report')
