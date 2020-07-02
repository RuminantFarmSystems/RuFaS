"""
RUFAS: Ruminant Farm Systems Model
File name: life_cycle_report.py
Description: Report for the life cycle submodule.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
            Katrina Wang, kw433@cornell.edu
"""
from .base_report import BaseReport
from .base_report_driver import BaseReportDriver
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
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

            self.herd_structure = {
                'year': ['time.cal_year', '', []],
                'j_day': ['time.day', '', []],
                'calf_num': ['life_cycle_manager.calf_num', '', []],
                'calf_percent': ['life_cycle_manager.calf_percent', '%', []],
                'heiferI_num': ['life_cycle_manager.heiferI_num', '', []],
                'heiferI_percent': ['life_cycle_manager.heiferI_percent', '%', []],
                'heiferII_num': ['life_cycle_manager.heiferII_num', '', []],
                'heiferII_percent': ['life_cycle_manager.heiferII_percent', '%', []],
                'heiferIII_num': ['life_cycle_manager.heiferIII_num', '', []],
                'heiferIII_percent': ['life_cycle_manager.heiferIII_percent', '%', []],
                'cow_num': ['life_cycle_manager.cow_num', '', []],
                'cow_percent': ['life_cycle_manager.cow_percent', '%', []],}

            
            for parity in LifeCycleManager.parity_num:
                self.herd_structure['cow_num_for_parity: ' + str(parity)] = ['life_cycle_manager.parity_num[' + str(parity) + ']', '', []]
                self.herd_structure['cow_percent_for_parity: ' + str(parity)] = ['life_cycle_manager.parity_percent[' + str(parity) + ']', '%', []]

            for cull_reason in LifeCycleManager.cull_reason_stats:
                self.herd_structure['cow_num_culled_for_reason: \'' + cull_reason + '\''] = \
                    ['life_cycle_manager.cull_reason_stats[\'' + cull_reason + '\']', '', []]
                self.herd_structure['cow_percent_culled_for_reason: \'' + cull_reason + '\''] = \
                    ['life_cycle_manager.cull_reason_stats_percent[\'' + cull_reason + '\']', '', []]
                        
            self.reproduction_performance = {
                'avg_service_rate': ['life_cycle_manager.avg_service_rate', '', []],
                'avg_conception_rate': ['life_cycle_manager.avg_conception_rate', '', []],
                'pregnancy_rate': ['life_cycle_manager.pregnancy_rate', '', []],
                'GnRH_injections': ['life_cycle_manager.GnRH_injection_num', '', []],
                'PGF_injections': ['life_cycle_manager.PGF_injection_num', '', []],
                'num_ai_21_days': ['life_cycle_manager.num_ai_21_days', '', []],
                'num_preg_check': ['life_cycle_manager.preg_check_num', '', []],
                'sold_calves': ['life_cycle_manager.total_calf_sold', '', []]
            }

            self.production_performance = {
                'cumulated_milk_production': ['life_cycle_manager.total_milk_production', 'kg', []]
            }

            self.preg = {
                'average_days_in_milk': ['life_cycle_manager.avg_days_in_milk', 'd', []],
                'average_days_in_preg': ['life_cycle_manager.avg_days_in_preg', 'd', []]
            }

            self.daily_variables = {**self.herd_structure, **self.reproduction_performance, **self.production_performance, **self.preg}
            
            self.annual_variables = {'year': ['time.cal_year', '', []]
                                     }

        def finalize(self, state, weather, time):
            print('herd done')
