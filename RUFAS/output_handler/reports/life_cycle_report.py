from pathlib import Path

from RUFAS.output_handler.reports import BaseReport
from .base_report_driver import BaseReportDriver
from .. import graphics


class LifeCycleReport(BaseReportDriver):
    def __init__(self, data):
        super().__init__(data)
        self.reports = {
            'individual_animal_report': self.IndividualAnimalReport(data['individual_animal_report']),
            'herd_report': self.HerdReport(data['herd_report'])
        }

    class IndividualAnimalReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []]
                                    }
            self.annual_variables = {'year': ['time.cal_year', '', []]
                                     }

        def finalize(self):
            print('individual done')

    class HerdReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []]}
            self.annual_variables = {'year': ['time.cal_year', '', []]
                                     }

        def finalize(self):
            print('herd done')
