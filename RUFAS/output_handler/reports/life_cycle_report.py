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
                'calf_percent': ['life_cycle_manager.calf_percent', '', []],
                'heiferI_num': ['life_cycle_manager.heiferI_num', '', []],
                'heiferI_percent': ['life_cycle_manager.heiferI_percent', '', []],
                'heiferII_num': ['life_cycle_manager.heiferII_num', '', []],
                'heiferII_percent': ['life_cycle_manager.heiferII_percent', '', []],
                'heiferIII_num': ['life_cycle_manager.heiferIII_num', '', []],
                'heiferIII_percent': ['life_cycle_manager.heiferIII_percent', '', []],
                'cow_num': ['life_cycle_manager.cow_num', '', []],
                'cow_percent': ['life_cycle_manager.cow_percent', '', []],
                'sold_heifer_num': ['life_cycle_manager.sold_heifer_num', '', []],
                'bought_heifer_num': ['life_cycle_manager.bought_heifer_num', '', []],
                'culled_heifer_num': ['life_cycle_manager.culled_heifer_num', '', []],
                'culled_cow_num': ['life_cycle_manager.culled_cow_num', '', []],
                'do_not_breed_cow_num': ['life_cycle_manager.do_not_breed_num', '', []],
            }
            
            for parity in LifeCycleManager.num_cow_for_parity:
                self.herd_structure['cow_num_for_parity_' + parity] = \
                    ['life_cycle_manager.num_cow_for_parity[\'' + parity + '\']', '', []]
                self.herd_structure['cow_percent_for_parity_' + parity] = \
                    ['life_cycle_manager.percent_cow_for_parity[\'' + parity + '\']', '', []]
                self.herd_structure['avg_age_for_parity_' + parity] = \
                    ['life_cycle_manager.avg_age_for_parity[\'' + parity + '\']', '', []]
                self.herd_structure['avg_age_for_calving_' + parity] = \
                    ['life_cycle_manager.avg_age_for_calving[\'' + parity + '\']', '', []]

            for cull_reason in LifeCycleManager.cull_reason_stats:
                self.herd_structure[cull_reason + '_num'] = \
                    ['life_cycle_manager.cull_reason_stats[\'' + cull_reason + '\']', '', []]
            
            for milking_satge in LifeCycleManager.num_cow_for_lactation_stage:
                self.herd_structure['stage_' + str(milking_satge)] = \
                    ['life_cycle_manager.num_cow_for_lactation_stage[\'' + str(milking_satge) + '\']', '', []]
                        
            self.reproduction_performance = {
                'CIDR_count': ['life_cycle_manager.CIDR_count', '', []],
                'GnRH_injections_heifer': ['life_cycle_manager.GnRH_injection_num_h', '', []],
                'PGF_injections_heifer': ['life_cycle_manager.PGF_injection_num_h', '', []],
                'semen_num_dairy_conventional_heifer': ['life_cycle_manager.semen_num_dairy_conventional_h', '', []],
                'semen_num_dairy_sexed_heifer': ['life_cycle_manager.semen_num_dairy_sexed_h', '', []],
                'semen_num_beef_conventional_heifer': ['life_cycle_manager.semen_num_beef_conventional_h', '', []],
                'semen_num_beef_sexed_heifer': ['life_cycle_manager.semen_num_beef_sexed_h', '', []],
                'ai_num_heifer': ['life_cycle_manager.ai_num_h', '', []],
                'preg_check_num_heifer': ['life_cycle_manager.preg_check_num_h', '', []],
                'ed_period_heifer': ['life_cycle_manager.ed_period_h', '', []],
                'avg_conception_rate_heifer': ['life_cycle_manager.avg_conception_rate_heifer', '', []],
                'avg_service_rate_heifer': ['life_cycle_manager.avg_service_rate_heifer', '', []],
                'pregnancy_rate_heifer': ['life_cycle_manager.pregnancy_rate_heifer', '', []],
                'GnRH_injections': ['life_cycle_manager.GnRH_injection_num', '', []],
                'PGF_injections': ['life_cycle_manager.PGF_injection_num', '', []],
                'semen_num_dairy_conventional': ['life_cycle_manager.semen_num_dairy_conventional', '', []],
                'semen_num_dairy_sexed': ['life_cycle_manager.semen_num_dairy_sexed', '', []],
                'semen_num_beef_conventional': ['life_cycle_manager.semen_num_beef_conventional', '', []],
                'semen_num_beef_sexed': ['life_cycle_manager.semen_num_beef_sexed', '', []],
                'ai_num': ['life_cycle_manager.ai_num', '', []],
                'preg_check_num': ['life_cycle_manager.preg_check_num', '', []],
                'ed_period': ['life_cycle_manager.ed_period', '', []],
                'avg_conception_rate': ['life_cycle_manager.avg_conception_rate', '', []],
                'avg_service_rate': ['life_cycle_manager.avg_service_rate', '', []],
                'pregnancy_rate': ['life_cycle_manager.pregnancy_rate', '', []],
                'sold_dairy_male_calf_num': ['life_cycle_manager.sold_dairy_male_calf_num', '', []],
                'sold_dairy_female_calf_num': ['life_cycle_manager.sold_dairy_female_calf_num', '', []],
                'sold_beef_male_calf_num': ['life_cycle_manager.sold_beef_male_calf_num', '', []],
                'sold_beef_female_calf_num': ['life_cycle_manager.sold_beef_female_calf_num', '', []],
                'culled_heifer_age': ['life_cycle_manager.culled_heifer_age', '', []],
                'heifer_open_time': ['life_cycle_manager.heifer_open_time', '', []],
                'produced_female_num': ['life_cycle_manager.produced_female_num', '', []],
                'died_female_calf_num': ['life_cycle_manager.died_female_calf_num', '', []]
            }

            self.production_performance = {
                'cumulated_milk_production': ['life_cycle_manager.daily_milk_production', '', []]
            }

            self.preg = {
                'open_cow_num': ['life_cycle_manager.open_cow_num', '', []],
                'non_preg_cow_percent': ['life_cycle_manager.non_preg_cow_percent', '', []],
                'preg_cow_num': ['life_cycle_manager.preg_cow_num', '', []],
                'preg_cow_percent': ['life_cycle_manager.preg_cow_percent', '', []],
                'milking_cow_num': ['life_cycle_manager.milking_cow_num', '', []],
                'milking_cow_percent': ['life_cycle_manager.milking_cow_percent', '', []],
                'dry_cow_num': ['life_cycle_manager.dry_cow_num', '', []],
                'dry_cow_percent': ['life_cycle_manager.dry_cow_percent', '', []],
                'average_days_in_milk': ['life_cycle_manager.avg_days_in_milk', '', []],
                'average_days_in_preg': ['life_cycle_manager.avg_days_in_preg', '', []],
                'average_cow_body_weight': ['life_cycle_manager.avg_cow_body_weight', '', []],
                'average_parity_number': ['life_cycle_manager.avg_parity_num', '', []]
            }

            self.average_animal_profile = {
                'avg_calving_interval': ['life_cycle_manager.avg_calving_interval', '', []],
                'avg_breeding_to_preg_time': ['life_cycle_manager.avg_breeding_to_preg_time', '', []],
                'avg_heifer_culling_age': ['life_cycle_manager.avg_heifer_culling_age', '', []],
                'avg_cow_culling_age': ['life_cycle_manager.avg_cow_culling_age', '', []],
                'avg_mature_body_weight': ['life_cycle_manager.avg_mature_body_weight', '', []],
                'daily_calf_body_weight_sum': ['life_cycle_manager.total_body_weight_calf', '', []],
                'daily_heifer_body_weight_sum': ['life_cycle_manager.total_body_weight_heifer', '', []],
                'daily_milking_cow_DMI_sum': ['life_cycle_manager.total_lactating_DMI', '', []],
                'daily_dry_cow_DMI_sum': ['life_cycle_manager.total_dry_DMI', '', []],
                'daily_culled_cow_body_weight_sum': ['life_cycle_manager.total_body_weight_culled_cow', '', []]
            }

            self.econmic_cal = {
                'cost_bought_heifer': ['life_cycle_manager.cost_bought_heifer', '', []],
                'cost_sold_heifer': ['life_cycle_manager.sold_heifer_cost', '', []],
                'income_sold_heifer': ['life_cycle_manager.income_sold_heifer', '', []],
                'income_sold_dairy_male_calf': ['life_cycle_manager.income_sold_dairy_male_calf', '', []],
                'income_sold_dairy_female_calf': ['life_cycle_manager.income_sold_dairy_female_calf', '', []],
                'income_sold_beef_male_calf': ['life_cycle_manager.income_sold_beef_male_calf', '', []],
                'income_sold_beef_female_calf': ['life_cycle_manager.income_sold_beef_female_calf', '', []],
                'income_culled_heifer': ['life_cycle_manager.income_culled_heifer', '', []],
                'income_culled_cow': ['life_cycle_manager.income_culled_cow', '', []],
                'income_milk': ['life_cycle_manager.income_milk', '', []],
                'cost_hormone': ['life_cycle_manager.cost_hormone', '', []],
                'cost_ed': ['life_cycle_manager.cost_ed', '', []],
                'cost_ai': ['life_cycle_manager.cost_ai', '', []],
                'cost_semen': ['life_cycle_manager.cost_semen', '', []],
                'cost_pc': ['life_cycle_manager.cost_pc', '', []],
                'cost_feed_milking_cow': ['life_cycle_manager.cost_feed_milking_cow', '', []],
                'cost_feed_dry_cow': ['life_cycle_manager.cost_feed_dry_cow', '', []],
                'cost_repro_cow': ['life_cycle_manager.repro_cost_cow', '', []],                
                'milk_income_over_feed_cost': ['life_cycle_manager.milk_income_over_feed_cost', '', []],
                'cost_hormone_heifer': ['life_cycle_manager.cost_hormone_heifer', '', []],
                'cost_ed_heifer': ['life_cycle_manager.cost_ed_heifer', '', []],
                'cost_ai_heifer': ['life_cycle_manager.cost_ai_heifer', '', []],
                'cost_semen_heifer': ['life_cycle_manager.cost_semen_heifer', '', []],
                'cost_pc_heifer': ['life_cycle_manager.cost_pc_heifer', '', []],
                'cost_repro_heifer': ['life_cycle_manager.repro_cost_heifer', '', []],
                'cost_feed_calf': ['life_cycle_manager.cost_feed_calf', '', []],
                'cost_feed_heifer': ['life_cycle_manager.cost_feed_heifer', '', []],
                'cost_feed': ['life_cycle_manager.feed_cost', '', []],
                'net_return': ['life_cycle_manager.net_return', '', []],
                'net_return_last_year': ['life_cycle_manager.net_return_last_year', '', []],
                'cost_hormone_heifer_more': ['life_cycle_manager.cost_hormone_heifer_more', '', []],
                'cost_ed_heifer_more': ['life_cycle_manager.cost_ed_heifer_more', '', []],
                'cost_ai_heifer_more': ['life_cycle_manager.cost_ai_heifer_more', '', []],
                'cost_semen_heifer_more': ['life_cycle_manager.cost_semen_heifer_more', '', []],
                'cost_pc_heifer_more': ['life_cycle_manager.cost_pc_heifer_more', '', []],
                'cost_repro_heifer_more': ['life_cycle_manager.repro_cost_heifer_more', '', []],
                'cost_feed_calf_more': ['life_cycle_manager.cost_feed_calf_more', '', []],
                'cost_feed_heifer_more': ['life_cycle_manager.cost_feed_heifer_more', '', []],
                'cost_feed_more': ['life_cycle_manager.feed_cost_more', '', []],
                'net_return_more_heifer': ['life_cycle_manager.net_return_more_heifer', '', []],
                'net_return_more_heifer_last_year': ['life_cycle_manager.net_return_more_heifer_last_year', '', []],
            }

            for parity in LifeCycleManager.avg_calving_to_preg_time:
                self.average_animal_profile['avg_calving_to_preg_time_for_parity_' + parity] = \
                    ['life_cycle_manager.avg_calving_to_preg_time[\'' + parity + '\']', '', []]

            for parity in LifeCycleManager.cow_open_time:
                self.reproduction_performance['cow_open_time_for_parity_' + parity] = \
                    ['life_cycle_manager.cow_open_time[\'' + parity + '\']', '', []]

            for parity in LifeCycleManager.culled_cow_dim:
                self.reproduction_performance['culled_cow_dim_for_parity_' + parity] = \
                    ['life_cycle_manager.culled_cow_dim[\'' + parity + '\']', '', []]

            self.genetic_performance = {
                'net_merit_cow': ['life_cycle_manager.avg_net_merit_cow', '', []],
                'net_merit_heifer': ['life_cycle_manager.avg_net_merit_heifer', '', []],
            }

            self.last_year_avg_vars = {
                'culling_rate': ['life_cycle_manager.cull_rate', '%', []],
                'sold_calf_total_last_year': ['life_cycle_manager.sold_calf_total_last_year', '', []],
                'sold_dairy_male_calf_num_last_year': ['life_cycle_manager.sold_dairy_male_calf_num_last_year', '', []],
                'sold_dairy_female_calf_num_last_year': ['life_cycle_manager.sold_dairy_female_calf_num_last_year', '', []],
                'sold_beef_male_calf_num_last_year': ['life_cycle_manager.sold_beef_male_calf_num_last_year', '', []],
                'sold_beef_female_calf_num_last_year': ['life_cycle_manager.sold_beef_female_calf_num_last_year', '', []],
                'sold_heifer_last_year': ['life_cycle_manager.sold_heifer_last_year', '', []],
                'bought_heifer_last_year': ['life_cycle_manager.bought_heifer_last_year', '', []],
                'culled_heifer_last_year': ['life_cycle_manager.culled_heifer_last_year', '', []]
            }

            self.daily_variables = {
                **self.herd_structure, 
                **self.reproduction_performance, 
                **self.production_performance, 
                **self.preg,
                **self.average_animal_profile,
                **self.econmic_cal,
                **self.genetic_performance,
                **self.last_year_avg_vars
            }
            
            self.annual_variables = {'year': ['time.calendar_year', '', []]}
