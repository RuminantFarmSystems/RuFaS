"""
RUFAS: Ruminant Farm Systems Model
File name: life_cycle_report.py
Description: Report for the life cycle submodule.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
            Katrina Wang, kw433@cornell.edu
"""
from .base_report import BaseReport
from .base_report_driver import BaseReportDriver
import json


class LifeCycleReport(BaseReportDriver):
    def __init__(self, data):
        super().__init__(data)
        self.reports = {
            'individual_animal_report':
                self.IndividualAnimalReport(data['individual_animal_report']),
            'herd_report': self.HerdReport(data['herd_report'])
        }

    class IndividualAnimalReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)
            self.num_animals = data['num_animals']

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []]
                                    }
            self.annual_variables = {'year': ['time.cal_year', '', []]
                                     }

        def finalize(self, state, weather, time):
            output = state.animal_management.get_life_cycle_output(
                self.num_animals)
            with open(str(self.csv_dir) + '/' + self.report_name + '.json',
                      'w') as outfile:
                json.dump(output, outfile, sort_keys=True, indent=4)

    class HerdReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.daily_variables = {'year': ['time.cal_year', '', []],
                                    'j_day': ['time.day', '', []]}
            self.annual_variables = {'year': ['time.cal_year', '', []]
                                     }

        def finalize(self, state, weather, time):
            print('herd done')
