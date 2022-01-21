"""
RUFAS: Ruminant Farm Systems Model
File name: life_cycle_report.py
Description: Report for the life cycle submodule.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
            Katrina Wang, kw433@cornell.edu
"""
from .. import graphics
from .base_report import BaseReport
from .base_report_driver import BaseReportDriver
from RUFAS.routines.animal.life_cycle.life_cycle import LifeCycleManager
import json


class LifeCycleReport(BaseReportDriver):
    def __init__(self, data):
        super().__init__(data)
        self.reports = {
            'initialization_db_summary':
                self.InitializationDBSummary(data['initialization_db_summary']),
            'individual_animal_report':
                self.IndividualAnimalReport(data['individual_animal_report']),
            'herd_report': self.HerdReport(data['herd_report'])
        }

    class InitializationDBSummary(BaseReport):
        def __init__(self, data):
            super().__init__(data)

        def finalize(self, state, weather, time):
            initialize_db_summary = \
                state.animal_management.get_initialize_db_summary()
            with open(str(self.csv_dir) + '/' + self.report_name + '.json',
                      'w') as outfile:
                json.dump(initialize_db_summary, outfile, sort_keys=True, indent=4)

        def initialize(self):
            pass

        def daily_update(self, state, weather, time):
            pass

        def annual_update(self, state, weather, time):
            pass

        def write_annual_report(self):
            pass

        def produce_report_graphics(self):
            pass

    class IndividualAnimalReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)
            self.num_animals = data['num_animals']
            self.animals = []

        def finalize(self, state, weather, time):
            self.animals, output = state.animal_management.get_life_cycle_output(
                self.num_animals)
            with open(str(self.csv_dir) + '/' + self.report_name + '.json',
                      'w') as outfile:
                json.dump(output, outfile, sort_keys=True, indent=4)

        def produce_report_graphics(self):
            # super().produce_report_graphics()
            graphics.individual_animal_graphics(self)

        def initialize(self):
            pass

        def daily_update(self, state, weather, time):
            pass

        def annual_update(self, state, weather, time):
            pass

        def write_annual_report(self):
            pass

    class HerdReport(BaseReport):
        def __init__(self, data):
            super().__init__(data)

            self.herd_structure = {
                'year': ['time.calendar_year', '', []],
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
                'cow_percent': ['life_cycle_manager.cow_percent', '%', []],
                'sold_heifer_num': ['life_cycle_manager.sold_heifer_num', '', []],
                'bought_heifer_num': ['life_cycle_manager.bought_heifer_num', '', []],
                'culled_heifer_num': ['life_cycle_manager.culled_heifer_num', '', []],
                'culled_cow_num': ['life_cycle_manager.culled_cow_num', '', []],
            }
            
            for parity in LifeCycleManager.num_cow_for_parity:
                self.herd_structure['cow_num_for_parity_' + parity] = \
                    ['life_cycle_manager.num_cow_for_parity[\'' + parity + '\']', '', []]
                self.herd_structure['cow_percent_for_parity_' + parity] = \
                    ['life_cycle_manager.percent_cow_for_parity[\'' + parity + '\']', '%', []]
                self.herd_structure['avg_age_for_parity_' + parity] = \
                    ['life_cycle_manager.avg_age_for_parity[\'' + parity + '\']', 'd', []]
                self.herd_structure['avg_age_for_calving_' + parity] = \
                    ['life_cycle_manager.avg_age_for_calving[\'' + parity + '\']', 'd', []]

            for cull_reason in LifeCycleManager.cull_reason_stats:
                self.herd_structure[cull_reason + '_num'] = \
                    ['life_cycle_manager.cull_reason_stats[\'' + cull_reason + '\']', '', []]
                self.herd_structure[cull_reason + '_percent'] = \
                    ['life_cycle_manager.cull_reason_stats_percent[\'' + cull_reason + '\']', '', []]
                        
            self.reproduction_performance = {
                'CIDR_count': ['life_cycle_manager.CIDR_count', '', []],
                'GnRH_injections_heifer': ['life_cycle_manager.GnRH_injection_num_h', '', []],
                'PGF_injections_heifer': ['life_cycle_manager.PGF_injection_num_h', '', []],
                'ai_num_heifer': ['life_cycle_manager.ai_num_h', '', []],
                'preg_check_num_heifer': ['life_cycle_manager.preg_check_num_h', '', []],
                'ed_period_heifer': ['life_cycle_manager.ed_period_h', '', []],
                'GnRH_injections': ['life_cycle_manager.GnRH_injection_num', '', []],
                'PGF_injections': ['life_cycle_manager.PGF_injection_num', '', []],
                'ai_num': ['life_cycle_manager.ai_num', '', []],
                'preg_check_num': ['life_cycle_manager.preg_check_num', '', []],
                'ed_period': ['life_cycle_manager.ed_period', '', []],
                'avg_conception_rate': ['life_cycle_manager.avg_conception_rate', '', []],
                'avg_service_rate': ['life_cycle_manager.avg_service_rate', '', []],
                'pregnancy_rate': ['life_cycle_manager.pregnancy_rate', '', []],
                'sold_calf_num': ['life_cycle_manager.sold_calf_num', '', []]
            }

            self.production_performance = {
                'cumulated_milk_production': ['life_cycle_manager.daily_milk_production', 'kg', []]
            }

            self.preg = {
                'open_cow_num': ['life_cycle_manager.open_cow_num', '', []],
                'non_preg_cow_percent': ['life_cycle_manager.non_preg_cow_percent', '%', []],
                'preg_cow_num': ['life_cycle_manager.preg_cow_num', '', []],
                'preg_cow_percent': ['life_cycle_manager.preg_cow_percent', '%', []],
                'milking_cow_num': ['life_cycle_manager.milking_cow_num', '', []],
                'milking_cow_percent': ['life_cycle_manager.milking_cow_percent', '%', []],
                'dry_cow_num': ['life_cycle_manager.dry_cow_num', '', []],
                'dry_cow_percent': ['life_cycle_manager.dry_cow_percent', '%', []],
                'average_days_in_milk': ['life_cycle_manager.avg_days_in_milk', 'd', []],
                'average_days_in_preg': ['life_cycle_manager.avg_days_in_preg', 'd', []],
                'average_cow_body_weight': ['life_cycle_manager.avg_cow_body_weight', 'kg', []],
                'average_parity_number': ['life_cycle_manager.avg_parity_num', '', []]
            }

            self.average_animal_profile = {
                'avg_caving_interval': ['life_cycle_manager.avg_calving_interval', 'd', []],
                'avg_breeding_to_preg_time': ['life_cycle_manager.avg_breeding_to_preg_time', 'd', []],
                'avg_heifer_culling_age': ['life_cycle_manager.avg_heifer_culling_age', 'd', []],
                'avg_cow_culling_age': ['life_cycle_manager.avg_cow_culling_age', 'd', []],
                'avg_mature_body_weight': ['life_cycle_manager.avg_mature_body_weight', 'kg', []],
            }

            for parity in LifeCycleManager.avg_calving_to_preg_time:
                self.average_animal_profile['avg_calving_to_preg_time_for_parity_' + parity] = \
                    ['life_cycle_manager.avg_calving_to_preg_time[\'' + parity + '\']', 'd', []]

            self.daily_variables = {
                **self.herd_structure, 
                **self.reproduction_performance, 
                **self.production_performance, 
                **self.preg,
                **self.average_animal_profile
            }
            
            self.annual_variables = {'year': ['time.calendar_year', '', []]}
