"""
RUFAS: Ruminant Farm Systems Model
File name: life_cycle.py
Description: The class which manages the life cycle of the animals. This
    includes storing all information necessary for the simulation, initializing
    the herd to start the simulation at a steady state, updating the animals
    for each day, and providing end-of-simulation statistics and graphs.
Author(s): Manfei Li, mli497@wisc.edu
           Militsa Sotirova, militsasotirova@gmail.com
"""
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_initialization import AnimalInitialization
from RUFAS.routines.animal.life_cycle import animal_events_constants as const
import numpy as np

class LifeCycleManager:
    """
    Manages the life cycles of the animals.
    """
    # statistics
    sold_heifers = []
    culled_heifers = []
    culled_cows = []

    calf_num = 0
    calf_percent = 0
    heiferI_num = 0
    heiferI_percent = 0
    heiferII_num = 0
    heiferII_percent = 0
    heiferIII_num = 0
    heiferIII_percent = 0
    cow_num = 0
    cow_percent = 0
    sold_calf_male_num = 0
    sold_calf_female_num = 0
    sold_calf_crossbred_male_num = 0
    sold_calf_crossbred_female_num = 0
    sold_heifer_num = 0
    bought_heifer_num = 0
    culled_heifer_num = 0
    culled_cow_num = 0
    do_not_breed_num = 0

    num_cow_for_parity = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    percent_cow_for_parity = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    avg_age_for_parity = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    avg_age_for_calving = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    num_cow_for_lactation_stage = {
        '1': 0,
        '2': 0,
        '3': 0,
        '4': 0,
        '5': 0,
        '6': 0,
        '7': 0,
        '8': 0
    }
    preg_check_num_h = 0
    preg_check_num = 0
    CIDR_count = 0
    GnRH_injection_num_h = 0
    PGF_injection_num_h = 0
    GnRH_injection_num = 0
    PGF_injection_num = 0

    open_cow_num = 0
    dry_cow_num = 0
    milking_cow_num = 0
    preg_cow_num = 0
    dry_cow_percent = 0
    milking_cow_percent = 0
    preg_cow_percent = 0
    non_preg_cow_percent = 0
    daily_milk_production = 0
    avg_days_in_milk = 0
    avg_days_in_preg = 0
    avg_cow_body_weight = 0
    avg_parity_num = 0
    avg_calving_interval = 0
    avg_breeding_to_preg_time = 0
    avg_calving_to_preg_time = {
        '1': 0,
        '2': 0,
        '3': 0,
        'greater_than_3': 0
    }
    avg_heifer_culling_age = 0
    avg_cow_culling_age = 0
    avg_mature_body_weight = 0

    cull_reason_stats = {
        const.DEATH_CULL: 0,
        const.LOW_PROD_CULL: 0,
        const.LAMENESS_CULL: 0,
        const.INJURY_CULL: 0,
        const.MASTITIS_CULL: 0,
        const.DISEASE_CULL: 0,
        const.UDDER_CULL: 0,
        const.UNKNOWN_CULL: 0
    }
    cull_reason_stats_range = {}
    parity_culling_stats_range = {}

    ai_num_h = 0
    semen_num_h = 0
    ed_period_h = 0
    ai_num = 0
    semen_num = 0
    ed_period = 0

    count_21_days = 0
    count_21_period = 0

    num_ai_21_days = 0
    num_cow_open_acc_21_days = 0
    service_rate_each_21_d = 0
    num_preg_21_days = 0
    conception_rate_each_21_d = 0
    avg_service_rate = 0
    avg_conception_rate = 0
    pregnancy_rate = 0
    service_rate_21_d = []
    conception_rate_21_d = []

    num_ai_21_days_heifer = 0
    num_heifer_open_acc_21_days = 0
    service_rate_each_21_d_heifer = 0
    num_preg_21_days_heifer = 0
    conception_rate_each_21_d_heifer = 0
    avg_service_rate_heifer = 0
    avg_conception_rate_heifer = 0
    pregnancy_rate_heifer = 0
    service_rate_21_d_heifer = []
    conception_rate_21_d_heifer = []
    culled_heifer_age = []
    heifer_open_time = []
    culled_cow_dim = {
        '1': [],
        '2': [],
        '3': [],
        'greater_than_3': []
    }
    cow_open_time = {
        '1': [],
        '2': [],
        '3': [],
        'greater_than_3': []
    }

    total_body_weight_calf = 0
    total_body_weight_heifer = 0
    total_lactating_DMI = 0
    total_dry_DMI = 0
    total_body_weight_culled_cow = 0

    sold_heifer_cost = 0
    sold_heifer_calf_cost = 0
    sold_heifer_hormone_cost = 0
    sold_heifer_ed_cost = 0
    sold_heifer_ai_cost = 0
    sold_heifer_semen_cost = 0
    sold_heifer_pc_cost = 0
    sold_heifer_feed_cost = 0

    cost_hormone_heifer = 0
    cost_hormone = 0
    cost_ed_heifer = 0
    cost_ed = 0
    cost_ai_heifer = 0
    cost_ai = 0
    cost_semen_heifer = 0
    cost_semen = 0
    cost_pc_heifer = 0
    cost_pc = 0
    cost_hormone_heifer_more = 0
    cost_ed_heifer_more = 0
    cost_ai_heifer_more = 0
    cost_semen_heifer_more = 0
    cost_pc_heifer_more = 0
    cost_feed_calf_more = 0
    cost_feed_heifer_more = 0
    cost_bought_heifer = 0
    cost_feed_calf = 0
    cost_feed_heifer = 0
    cost_feed_milking_cow = 0
    cost_feed_dry_cow = 0
    income_sold_female_calf = 0
    income_sold_male_calf = 0
    income_sold_heifer = 0
    income_culled_heifer = 0
    income_culled_cow = 0
    income_milk = 0

    repro_cost_heifer = 0
    repro_cost_heifer_more = 0
    repro_cost_cow = 0
    feed_cost = 0
    feed_cost_more = 0
    milk_income_over_feed_cost = 0
    net_return = 0
    net_return_more_heifer = 0
    

    config = None

    replacement_market = []

    herd_num = 0

    animal_initializer = None

    def __init__(self, data):
        """
        Initializes the necessary configuration data.

        Args:
            data: life cycle data from the input JSON file
        """
        self.config = data
        self.avg_daily_cow_milking = 0
        self.initialize_db_summary = {}
        self.avg_CI = 0

    def initialize_herd(self, herd_num, calf_num, heiferI_num, heiferII_num,
                        heiferIII_num, cow_num, replace_num, herd_init, breed,
                        config):
        """
        Generates a replacement herd to simulate the market, for the herd to get
         replacements. Initializes the herd.

        Args:
            breed: TODO: needs description
            config: stores (among other things) information on whether the seed
                has been set by the user
            herd_init: boolean - true to populate database with new animals,
                false to use current database
            herd_num: what the number of cows should be maintained at
            calf_num: the number of calves to start the simulation with
            heiferI_num: the number of heiferIs to start the simulation with
            heiferII_num: the number of heiferIIs to start the simulation with
            heiferIII_num: the number of heiferIIIs to start the simulation with
            cow_num: the number of cows to start the simulation with
            replace_num: replacements in the market

        Returns:
            calves: list of calves for the simulation
            heiferIs: list of heiferIs for the simulation
            heiferIIs: list of heiferIIs for the simulation
            heiferIIIs: list of heiferIIIs for the simulation
            cows: list of cows for the simulation
        """
        self.animal_initializer = AnimalInitialization(self.config['calving_interval'], breed,
                                                       config.set_seed, herd_init)

        if self.config['use_input_calving_interval']:
            self.avg_CI = self.config['calving_interval']
        else:
            self.initialize_db_summary = \
                self.animal_initializer.initialization_db_summary()
            self.avg_CI = self.initialize_db_summary['cow_avg_CI']
        self.herd_num = herd_num

        calves = self.animal_initializer.get_calves(calf_num, breed)
        for calf in calves:
            calf.events.add_event(calf.days_born, 0, const.INIT_HERD)

        heiferIs = self.animal_initializer.get_heiferIs(heiferI_num, breed)
        for heiferI in heiferIs:
            heiferI.events.add_event(heiferI.days_born, 0, const.INIT_HERD)

        heiferIIs = self.animal_initializer.get_heiferIIs(heiferII_num, breed)
        for heiferII in heiferIIs:
            heiferII.events.add_event(heiferII.days_born, 0, const.INIT_HERD)

        heiferIIIs = self.animal_initializer.get_heiferIIIs(heiferIII_num, breed)
        for heiferIII in heiferIIIs:
            heiferIII.events.add_event(heiferIII.days_born, 0, const.INIT_HERD)

        cows = self.animal_initializer.get_cows(cow_num, breed)
        for cow in cows:
            cow.events.add_event(cow.days_born, 0, const.INIT_HERD)

        self.replacement_market = self.animal_initializer.get_replacement_cows(replace_num, breed)
        return calves, heiferIs, heiferIIs, heiferIIIs, cows

    def daily_update(self, date, calves, heiferIs, heiferIIs,
                     heiferIIIs, cows):
        """
        Updates the status of the animals.

        Args:
            cows: list of Cow objects to be updated
            heiferIIIs: list of HeiferIII objects to be updated
            heiferIIs: list of HeiferII objects to be updated
            heiferIs: list of HeiferI objects to be updated
            calves: list of Calf objects to be updated
            date: day number

        Returns:
            animals_added: list of animals added from replacement herd
            ids_removed: list of animal ids that were removed during this day
            calves_born: list of calves that were born during this day
            calves: updated list of calves
            heiferIs: updated list of heiferIs
            heiferIIs: updated list of heiferIIs
            heiferIIIs: updated list of heiferIIIs
            cows: updated list of cows

        """
        ids_removed = []
        animals_added = []
        calves_born = []

        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0
        self.sold_calf_male_num = 0
        self.sold_calf_female_num = 0
        self.sold_calf_crossbred_male_num = 0
        self.sold_calf_crossbred_female_num = 0
        self.sold_heifer_num = 0
        self.bought_heifer_num = 0
        self.culled_heifer_num = 0
        self.culled_cow_num = 0
        total_animal_num = 0

        self.preg_check_num_h = 0
        self.preg_check_num = 0
        self.CIDR_count = 0
        self.GnRH_injection_num_h = 0
        self.PGF_injection_num_h = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num = 0
        self.ai_num_h = 0
        self.semen_num_h = 0
        self.ed_period_h = 0
        self.ai_num = 0
        self.semen_num = 0
        self.ed_period = 0

        self.daily_milk_production = 0
        self.open_cow_num = 0
        self.preg_cow_num = 0
        self.milking_cow_num = 0
        self.dry_cow_num = 0
        self.avg_days_in_milk = 0
        self.avg_days_in_preg = 0
        self.avg_cow_body_weight = 0
        self.avg_parity_num = 0
        self.avg_calving_interval = 0
        self.avg_breeding_to_preg_time = 0
        self.avg_heifer_culling_age = 0
        self.avg_cow_culling_age = 0
        self.avg_mature_body_weight = 0
        self.do_not_breed_num = 0

        self.total_body_weight_calf = 0
        self.total_body_weight_heifer = 0
        self.total_lactating_DMI = 0
        self.total_dry_DMI = 0
        self.total_body_weight_culled_cow = 0

        preg_heifer_num = 0
        calving_interval_available_num = 0
        calving_age_available_num = {
            '1': 0,
            '2': 0,
            '3': 0,
            'greater_than_3': 0
        }
        calving_to_preg_time_available_num = {
            '1': 0,
            '2': 0,
            '3': 0,
            'greater_than_3': 0
        }

        self.cost_hormone_heifer = 0
        self.cost_hormone = 0
        self.cost_ed_heifer = 0
        self.cost_ed = 0
        self.cost_ai_heifer = 0
        self.cost_ai = 0
        self.cost_semen_heifer = 0
        self.cost_semen = 0
        self.cost_pc_heifer = 0
        self.cost_pc = 0
        self.cost_hormone_heifer_more = 0
        self.cost_ed_heifer_more = 0
        self.cost_ai_heifer_more = 0
        self.cost_semen_heifer_more = 0
        self.cost_pc_heifer_more = 0
        self.cost_feed_calf_more = 0
        self.cost_feed_heifer_more = 0
        self.cost_bought_heifer = 0
        self.cost_feed_calf = 0
        self.cost_feed_heifer = 0
        self.cost_feed_milking_cow = 0
        self.cost_feed_dry_cow = 0
        self.income_sold_female_calf = 0
        self.income_sold_male_calf = 0
        self.income_sold_heifer = 0
        self.income_culled_heifer = 0
        self.income_culled_cow = 0
        self.income_milk = 0

        self.repro_cost_heifer = 0
        self.repro_cost_heifer_more = 0
        self.repro_cost_cow = 0
        self.feed_cost = 0
        self.feed_cost_more = 0
        self.milk_income_over_feed_cost = 0
        self.net_return = 0
        self.net_return_more_heifer = 0
    
        self.sold_heifer_cost = 0
        self.sold_heifer_calf_cost = 0
        self.sold_heifer_hormone_cost = 0
        self.sold_heifer_ed_cost = 0
        self.sold_heifer_ai_cost = 0
        self.sold_heifer_semen_cost = 0
        self.sold_heifer_pc_cost = 0
        self.sold_heifer_feed_cost = 0

        self.culled_heifer_age = []
        self.heifer_open_time = []
        self.culled_cow_dim = {
            '1': [],
            '2': [],
            '3': [],
            'greater_than_3': []
        }
        self.cow_open_time = {
            '1': [],
            '2': [],
            '3': [],
            'greater_than_3': []
        }

        for parity in self.num_cow_for_parity:
            self.num_cow_for_parity[parity] = 0
            self.percent_cow_for_parity[parity] = 0
            self.avg_age_for_parity[parity] = 0
            self.avg_age_for_calving[parity] = 0
            self.avg_calving_to_preg_time[parity] = 0

        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats[cull_reason] = 0
        
        for milking_stage in self.num_cow_for_lactation_stage:
            self.num_cow_for_lactation_stage[milking_stage] = 0

        # calf to heiferI
        for index, calf in enumerate(calves):
            wean_day = calf.update(date)
            if wean_day:
                args = calf.get_calf_values()
                args.update({
                    'body_weight_history': calf.body_weight_history,
                    'pen_history': calf.pen_history,
                    'calf_cost':calf.calf_cost
                })
                new_heiferI = HeiferI(args)
                heiferIs.append(new_heiferI)
                del calves[index]
            else:
                self.calf_num += 1
                self.total_body_weight_calf += calf.body_weight
                total_animal_num, self.avg_mature_body_weight = \
                    self.calc_average(total_animal_num,
                                       self.avg_mature_body_weight, calf.mature_body_weight)

        # heiferI to heiferII, assign repro programs
        for index, heiferI in enumerate(heiferIs):
            second_stage = heiferI.update(date)
            if second_stage:
                args = heiferI.get_heiferI_values()
                args.update({
                    'body_weight_history': heiferI.body_weight_history,
                    'pen_history': heiferI.pen_history,
                    'calf_cost': heiferI.calf_cost,
                    'heifer_feed_cost': heiferI.heifer_feed_cost
                     })
                args.update(repro_program=AnimalBase.config['heifer_repro_method'])
                args.update(tai_method_h=AnimalBase.config['heifer_TAI_protocol'])
                args.update(synch_ed_method_h=AnimalBase.config['heifer_synchED_protocol'])
                new_heiferII = HeiferII(args)
                heiferIIs.append(new_heiferII)
                del heiferIs[index]
            else:
                self.heiferI_num += 1
                self.total_body_weight_heifer += heiferI.body_weight
                total_animal_num, self.avg_mature_body_weight = \
                    self.calc_average(total_animal_num,
                                       self.avg_mature_body_weight, heiferI.mature_body_weight)

        # heiferII to heiferIII
        for index, heiferII in enumerate(heiferIIs):
            cull_stage, third_stage = heiferII.update(date)
            if cull_stage:
                self.culled_heifer_num, self.avg_heifer_culling_age = \
                    self.calc_average(self.culled_heifer_num,
                                       self.avg_heifer_culling_age, heiferII.days_born)
                self.culled_heifer_age.append(heiferII.days_born) 
                self.culled_heifers.append(heiferII)
                del heiferIIs[index]
            elif third_stage:
                args = heiferII.get_heiferII_values()
                args.update({
                    'body_weight_history': heiferII.body_weight_history,
                    'pen_history': heiferII.pen_history,
                    'conceptus_weight': heiferII.conceptus_weight,
                    'calf_birth_weight': heiferII.calf_birth_weight,
                    'calf_cost': heiferII.calf_cost,
                    'heifer_feed_cost': heiferII.heifer_feed_cost,
                    'heifer_hormone_cost': heiferII.heifer_hormone_cost,
                    'heifer_ed_cost': heiferII.heifer_ed_cost,
                    'heifer_ai_semen_cost': heiferII.heifer_ai_semen_cost,
                    'heifer_pc_cost': heiferII.heifer_pc_cost
                })
                new_heiferIII = HeiferIII(args)
                heiferIIIs.append(new_heiferIII)
                del heiferIIs[index]
            else:
                self.heiferII_num += 1
                self.total_body_weight_heifer += heiferII.body_weight
                total_animal_num, self.avg_mature_body_weight = \
                    self.calc_average(total_animal_num,
                                       self.avg_mature_body_weight, heiferII.mature_body_weight)
                if heiferII.breeding_to_preg_time != 0:
                    preg_heifer_num, self.avg_breeding_to_preg_time = \
                        self.calc_average(preg_heifer_num,
                                           self.avg_breeding_to_preg_time,
                                           heiferII.breeding_to_preg_time)
                    if heiferII.days_in_preg == 1:
                        self.heifer_open_time.append(heiferII.breeding_to_preg_time)

                self.CIDR_count += heiferII.CIDR_count
                self.GnRH_injection_num_h += heiferII.GnRH_injections
                self.PGF_injection_num_h += heiferII.PGF_injections
                self.preg_check_num_h += heiferII.preg_diagnoses
                self.semen_num_h += heiferII.semen_num
                self.ai_num_h += heiferII.AI_times
                self.ed_period_h += heiferII.ED_days
               
                # caculate reproduction indications
            if date >= 1:
                if heiferII.days_born == heiferII.ai_day:
                    self.num_ai_21_days_heifer += 1
                if heiferII.days_in_preg == 0 and heiferII.days_born > AnimalBase.config['breeding_start_day_h']:
                    self.num_heifer_open_acc_21_days += 1
                if heiferII.days_in_preg == 1:
                    self.num_preg_21_days_heifer += 1   
        
        # Jan 12th by Yijing: added check for division of 0
        #caculate service rate and conception rate
        if date >= 106:
            self.count_21_days += 1
            if self.count_21_days % 21 == 0 and self.count_21_days != 0:
                self.count_21_period += 1
                if self.num_heifer_open_acc_21_days == 0:
                    self.service_rate_each_21_d_heifer = np.nan
                else:
                    self.service_rate_each_21_d_heifer = float(self.num_ai_21_days_heifer) / float(self.num_heifer_open_acc_21_days/21)
                
                if self.num_ai_21_days_heifer == 0:
                    self.conception_rate_each_21_d_heifer = np.nan
                else:
                    self.conception_rate_each_21_d_heifer = float(self.num_preg_21_days_heifer) / float(self.num_ai_21_days_heifer)
                
                self.num_ai_21_days_heifer = 0
                self.num_heifer_open_acc_21_days = 0
                self.num_preg_21_days_heifer = 0
                self.avg_service_rate_heifer, self.service_rate_21_d_heifer = self.moving_average(self.service_rate_each_21_d_heifer, 15, self.service_rate_21_d_heifer)
                self.avg_conception_rate_heifer, self.conception_rate_21_d_heifer = self.moving_average(self.conception_rate_each_21_d_heifer, 15, self.conception_rate_21_d_heifer)
                self.pregnancy_rate_heifer = self.avg_service_rate_heifer * self.avg_conception_rate_heifer

        # heiferIII to cow, assign repro programs
        for index, heiferIII in enumerate(heiferIIIs):

            # TODO why can cows be added to the list of HeiferIII's so that the
            #  following if statement is necessary?
            if type(heiferIII).__name__ == 'HeiferIII':
                cow_stage = heiferIII.update(date)
            else:
                cow_stage = heiferIII.update(date, self.avg_CI)

            if cow_stage:
                args = heiferIII.get_heiferIII_values()
                args.update({
                    'body_weight_history': heiferIII.body_weight_history,
                    'pen_history': heiferIII.pen_history,
                    'conceptus_weight': heiferIII.conceptus_weight,
                    'calf_birth_weight': heiferIII.calf_birth_weight,
                    'calf_cost': heiferIII.calf_cost,
                    'heifer_feed_cost': heiferIII.heifer_feed_cost,
                    'heifer_hormone_cost': heiferIII.heifer_hormone_cost,
                    'heifer_ed_cost': heiferIII.heifer_ed_cost,
                    'heifer_ai_semen_cost': heiferIII.heifer_ai_semen_cost,
                    'heifer_pc_cost': heiferIII.heifer_pc_cost
                     })
                args.update(repro_program=AnimalBase.config['cow_repro_method'])
                args.update(presynch_method=AnimalBase.config['cow_presynch_protocol'])
                args.update(tai_method_c=AnimalBase.config['cow_TAI_protocol'])
                args.update(resynch_method=AnimalBase.config['cow_resynch_protocol'])
                new_cow = Cow(args)
                cows.append(new_cow)
                del heiferIIIs[index]
            else:
                self.heiferIII_num += 1
                self.total_body_weight_heifer += heiferIII.body_weight
                total_animal_num, self.avg_mature_body_weight = \
                    self.calc_average(total_animal_num,
                                       self.avg_mature_body_weight, heiferIII.mature_body_weight)

        # if the number of heifers is more than needed for the herd, sell
        # those as replacement
        while len(heiferIIIs) + len(cows) > self.herd_num * 1.03 and len(heiferIIIs) > 0:
            removed = heiferIIIs.pop()
            self.sold_heifer_cost += removed.calf_cost + removed.heifer_feed_cost + removed.heifer_hormone_cost\
                + removed.heifer_ed_cost + removed.heifer_ai_semen_cost +removed.heifer_pc_cost
            self.sold_heifer_calf_cost += removed.calf_cost
            self.sold_heifer_hormone_cost += removed.heifer_hormone_cost
            self.sold_heifer_ed_cost += removed.heifer_ed_cost
            self.sold_heifer_ai_cost += removed.heifer_ai_semen_cost * 0.4
            self.sold_heifer_semen_cost += removed.heifer_ai_semen_cost * 0.6
            self.sold_heifer_pc_cost += removed.heifer_pc_cost
            self.sold_heifer_feed_cost += removed.heifer_feed_cost
            ids_removed.append(removed.id)
            self.sold_heifers.append(removed)
            self.sold_heifer_num += 1

        # if the number of heifers is less than needed for the herd,
        # buy replacement from the market
        while len(cows) + len(heiferIIIs) + self.bought_heifer_num < self.herd_num * 1.01 and \
                date > 1:
            self.replacement_market[0].events.add_event(
                self.replacement_market[0].days_born, date, const.ENTER_HERD)
            self.replacement_market[0].set_p_purchased()
            animals_added.append(self.replacement_market[0])
            self.bought_heifer_num += 1
            del self.replacement_market[0]

        # cow culling action and stats
        for index, cow in enumerate(cows):
            _, _, _, culled, new_born = cow.update(date, self.avg_CI)

            # culled cows, calculate slaughter value and record culling reasons
            if culled:
                if cow.cull_reason in self.cull_reason_stats_range:
                    self.cull_reason_stats_range[cow.cull_reason] += 1
                else:
                    self.cull_reason_stats_range[cow.cull_reason] = 1
                parity = cow.calves if cow.calves <= 3 else '4+'
                if cow.calves in self.parity_culling_stats_range:
                    self.parity_culling_stats_range[parity] += 1
                else:
                    self.parity_culling_stats_range[parity] = 1

                if cow.cull_reason == const.LOW_PROD_CULL:
                    if 0 < cow.calves <= 3:
                        self.culled_cow_dim[str(cow.calves)].append(cow.days_in_milk)
                    else:
                        self.culled_cow_dim['greater_than_3'].append(cow.days_in_milk) 

                self.culled_cows.append(cow)
                self.total_body_weight_culled_cow += cow.body_weight
                self.cull_reason_stats[cow.cull_reason] += 1
                self.culled_cow_num, self.avg_cow_culling_age = \
                    self.calc_average(self.culled_cow_num,
                                       self.avg_cow_culling_age, cow.days_born)

                ids_removed.append(cow.id)
                del cows[index]

            else:
                if cow.do_not_breed:
                    self.do_not_breed_num += 1

                # record average cow body weight, average parity number, and average mature body weight
                _, self.avg_cow_body_weight = self.calc_average(
                    self.cow_num, self.avg_cow_body_weight, cow.body_weight)
                self.cow_num, self.avg_parity_num = self.calc_average(
                    self.cow_num, self.avg_parity_num, cow.calves)
                total_animal_num, self.avg_mature_body_weight = \
                    self.calc_average(total_animal_num,
                                       self.avg_mature_body_weight, cow.mature_body_weight)

                if cow.milking:
                    # record daily total milk production, average days in milk
                    self.total_lactating_DMI += cow.DMIest
                    self.daily_milk_production += cow.estimated_daily_milk_produced
                    self.milking_cow_num, self.avg_days_in_milk = \
                        self.calc_average(self.milking_cow_num,
                                           self.avg_days_in_milk, cow.days_in_milk)
                else:
                    self.total_dry_DMI += cow.DMIest
                    self.dry_cow_num += 1

                if cow.days_in_milk > 50 and cow.days_in_preg == 0 and not cow.do_not_breed:
                    self.open_cow_num += 1

                if cow.days_in_milk > 0:
                    if cow.days_in_milk > 0 and cow.days_in_milk < 51:
                        milking_stage = 1
                        self.num_cow_for_lactation_stage['1'] += 1
                    elif cow.days_in_milk > 50 and cow.days_in_milk < 101:
                        milking_stage = 2
                        self.num_cow_for_lactation_stage['2'] += 1
                    elif cow.days_in_milk > 100 and cow.days_in_milk < 151:
                        milking_stage = 3
                        self.num_cow_for_lactation_stage['3'] += 1
                    elif cow.days_in_milk > 150 and cow.days_in_milk < 201:
                        milking_stage = 4
                        self.num_cow_for_lactation_stage['4'] += 1
                    elif cow.days_in_milk > 200 and cow.days_in_milk < 251:
                        milking_stage = 5
                        self.num_cow_for_lactation_stage['5'] += 1
                    elif cow.days_in_milk > 250 and cow.days_in_milk < 301:
                        milking_stage = 6
                        self.num_cow_for_lactation_stage['6'] += 1
                    elif cow.days_in_milk > 300 and cow.days_in_milk < 351:
                        milking_stage = 7
                        self.num_cow_for_lactation_stage['7'] += 1
                    else:
                        milking_stage = 8
                        self.num_cow_for_lactation_stage['8'] += 1

                if cow.days_in_preg > 0:
                    self.preg_cow_num, self.avg_days_in_preg = \
                        self.calc_average(self.preg_cow_num,
                                           self.avg_days_in_preg, cow.days_in_preg)

                if 0 < cow.calves <= 3:
                    self.num_cow_for_parity[str(cow.calves)], \
                    self.avg_age_for_parity[str(cow.calves)] = \
                        self.calc_average(
                            self.num_cow_for_parity[str(cow.calves)],
                            self.avg_age_for_parity[str(cow.calves)],
                            cow.days_born)
                    calving_age = cow.events.get_most_recent_date(const.NEW_BIRTH)
                    if calving_age != -1:
                        calving_age_available_num[str(cow.calves)], \
                        self.avg_age_for_calving[str(cow.calves)] = \
                            self.calc_average(
                                calving_age_available_num[str(cow.calves)],
                                self.avg_age_for_calving[str(cow.calves)],
                                calving_age)
                    if cow.calving_to_preg_time != 0:
                        calving_to_preg_time_available_num[str(cow.calves)], \
                        self.avg_calving_to_preg_time[str(cow.calves)] = \
                            self.calc_average(
                                calving_to_preg_time_available_num[str(cow.calves)],
                                self.avg_calving_to_preg_time[str(cow.calves)],
                                cow.calving_to_preg_time)
                        if cow.days_in_preg == 1:
                            self.cow_open_time[str(cow.calves)].append(cow.calving_to_preg_time) 
                else:
                    self.num_cow_for_parity['greater_than_3'], \
                    self.avg_age_for_parity['greater_than_3'] = self.calc_average(
                        self.num_cow_for_parity['greater_than_3'],
                        self.avg_age_for_parity['greater_than_3'], cow.days_born)
                    calving_age = cow.events.get_most_recent_date(const.NEW_BIRTH)
                    if calving_age != -1:
                        calving_age_available_num['greater_than_3'], \
                        self.avg_age_for_calving['greater_than_3'] = \
                            self.calc_average(
                                calving_age_available_num['greater_than_3'],
                                self.avg_age_for_calving['greater_than_3'],
                                calving_age)
                    if cow.calving_to_preg_time != 0:
                        calving_to_preg_time_available_num['greater_than_3'], \
                        self.avg_calving_to_preg_time['greater_than_3'] = \
                            self.calc_average(
                                calving_to_preg_time_available_num['greater_than_3'],
                                self.avg_calving_to_preg_time['greater_than_3'],
                                cow.calving_to_preg_time)
                        if cow.days_in_preg == 1:
                            self.cow_open_time['greater_than_3'].append(cow.calving_to_preg_time) 

                if cow.CI != 0:
                    calving_interval_available_num, \
                    self.avg_calving_interval = self.calc_average(
                        calving_interval_available_num,
                        self.avg_calving_interval, cow.CI)

                self.GnRH_injection_num += cow.GnRH_injections
                self.PGF_injection_num += cow.PGF_injections
                self.preg_check_num += cow.preg_diagnoses
                self.semen_num += cow.semen_num
                self.ai_num += cow.AI_times
                self.ed_period += cow.ED_days

            if new_born:
                args = {
                    'id': self.animal_initializer.next_id(),
                    'breed': 'HO',
                    'birth_date': date,
                    'days_born': 0,
                    'p_init': cow.p_gest_for_calf,
                    'birth_weight': cow.calf_birth_weight
                }
                # at parturition, the sum of P absorbed for gestation rqmts is
                # subtracted from the animal value. the sum of P absorbed for
                # gestation is equal to the initial animal P value for the calf
                # (A.1G.A.4)
                cow.p_animal = cow.p_animal - cow.p_gest_for_calf + \
                               cow.p_growth + cow.dP_reserves

                new_calf = Calf(args)
                cow.p_gest_for_calf = 0
                cow.calf_birth_weight = 0

                if not (new_calf.culled or new_calf.sold):
                    new_calf.events.add_event(
                        new_calf.days_born, date, const.ENTER_HERD)
                    # calves.append(new_calf)
                    calves_born.append(new_calf)
                if new_calf.sold:
                    if new_calf.breed == 'HO':
                        if new_calf.gender == 'male':
                            self.sold_calf_male_num += 1
                        else:
                            self.sold_calf_female_num += 1
                    if new_calf.breed == 'HO-AN':
                        if new_calf.gender == 'male':
                            self.sold_calf_crossbred_male_num += 1
                        else:
                            self.sold_calf_crossbred_female_num += 1  

            # caculate reproduction indications
            if date >= 1:
                if cow.days_born == cow.ai_day:
                    self.num_ai_21_days += 1
                if cow.days_in_preg == 0 and cow.days_in_milk > 50 and not cow.do_not_breed:
                    self.num_cow_open_acc_21_days += 1
                if cow.days_in_preg == 1:
                    self.num_preg_21_days += 1   
        
        # Jan 12th by Yijing: added check for division of 0
        #caculate service rate and conception rate
        if date >= 106:
            self.count_21_days += 1
            if self.count_21_days % 21 == 0 and self.count_21_days != 0:
                self.count_21_period += 1
                if self.num_cow_open_acc_21_days == 0:
                    self.service_rate_each_21_d = np.nan
                else:
                    self.service_rate_each_21_d = float(self.num_ai_21_days) / float(self.num_cow_open_acc_21_days/21)

                if self.num_ai_21_days == 0:
                    self.conception_rate_each_21_d = np.nan
                else:
                    self.conception_rate_each_21_d = float(self.num_preg_21_days) / float(self.num_ai_21_days)  
                self.num_ai_21_days = 0
                self.num_cow_open_acc_21_days = 0
                self.num_preg_21_days = 0
                self.avg_service_rate, self.service_rate_21_d = self.moving_average(self.service_rate_each_21_d, 15, self.service_rate_21_d)
                self.avg_conception_rate, self.conception_rate_21_d = self.moving_average(self.conception_rate_each_21_d, 15, self.conception_rate_21_d)
                self.pregnancy_rate = self.avg_service_rate * self.avg_conception_rate

        # income/cost calculation
        self.cost_hormone_heifer = 1.83 * self.GnRH_injection_num_h + 2.29 * self.PGF_injection_num_h + 12.53 * self.CIDR_count
        self.cost_ed_heifer = 0.11 * self.ed_period_h
        self.cost_ai_heifer = 10 * self.ai_num_h
        self.cost_semen_heifer = 15 * self.semen_num_h
        self.cost_pc_heifer = 4.37 * self.preg_check_num_h

        self.cost_hormone_heifer_more = 1.83 * self.GnRH_injection_num_h + 2.29 * self.PGF_injection_num_h + 12.53 * self.CIDR_count - self.sold_heifer_hormone_cost
        self.cost_ed_heifer_more = 0.11 * self.ed_period_h - self.sold_heifer_ed_cost
        self.cost_ai_heifer_more = 10 * self.ai_num_h - self.sold_heifer_ai_cost
        self.cost_semen_heifer_more = 15 * self.semen_num_h - self.sold_heifer_semen_cost
        self.cost_pc_heifer_more = 4.37 * self.preg_check_num_h - self.sold_heifer_pc_cost          

        self.cost_hormone = 1.83 * self.GnRH_injection_num + 2.29 * self.PGF_injection_num
        self.cost_ed = 0.11 * self.ed_period 
        self.cost_ai = 10 * self.ai_num
        self.cost_semen = 15 * self.semen_num
        self.cost_pc = 4.37 * self.preg_check_num

        self.cost_bought_heifer = 1500 * self.bought_heifer_num
        # consume milk, 10% of its BW
        self.cost_feed_calf = 0.2 * 0.1 * self.total_body_weight_calf
        self.cost_feed_calf_more = 0.2 * 0.1 * self.total_body_weight_calf - self.sold_heifer_calf_cost
        # $2.4 per day for average weight heifer
        self.cost_feed_heifer = 0.0068 * self.total_body_weight_heifer
        self.cost_feed_heifer_more = 0.0068 * self.total_body_weight_heifer - self.sold_heifer_feed_cost
        # $0.06-0.08 per lb DM
        self.cost_feed_milking_cow = 0.24 * self.total_lactating_DMI
        self.cost_feed_dry_cow = 0.24 * self.total_dry_DMI
        self.income_sold_female_calf = 120 * self.sold_heifer_num
        self.income_sold_male_calf = 50 * self.sold_calf_male_num
        self.income_sold_heifer = 1380 * self.sold_heifer_num
        self.income_culled_heifer = 124 * self.culled_heifer_num
        self.income_culled_cow = 1.49 * self.total_body_weight_culled_cow
        self.income_milk = 0.35 * self.daily_milk_production

        self.repro_cost_heifer = self.cost_hormone_heifer + self.cost_ed_heifer + self.cost_ai_heifer + \
            self.cost_semen_heifer + self.cost_pc_heifer 
        self.repro_cost_heifer_more = self.cost_hormone_heifer_more + self.cost_ed_heifer_more + self.cost_ai_heifer_more + \
            self.cost_semen_heifer_more + self.cost_pc_heifer_more 
        self.repro_cost_cow = self.cost_hormone + self.cost_ed + self.cost_ai + self.cost_semen + self.cost_pc
        
        self.feed_cost = self.cost_feed_calf + self.cost_feed_heifer + self.cost_feed_milking_cow + self.cost_feed_dry_cow
        self.feed_cost_more = self.cost_feed_calf_more + self.cost_feed_heifer_more + self.cost_feed_milking_cow + self.cost_feed_dry_cow
        self.milk_income_over_feed_cost = self.income_milk - self.cost_feed_milking_cow - self.cost_feed_dry_cow
        
        # Jan 12th by Yijing: Added income_sold_heifer
        # bought more than sold
        self.net_return = self.income_milk + self.income_sold_male_calf + self.income_sold_heifer + self.income_culled_heifer + self.income_culled_cow -\
             self.repro_cost_heifer - self.repro_cost_cow - self.feed_cost
        # sold more than bought
        self.net_return_more_heifer = self.income_milk + self.income_sold_male_calf + self.income_sold_heifer + self.income_culled_heifer + self.income_culled_cow -\
             self.repro_cost_heifer_more - self.repro_cost_cow - self.feed_cost_more
    
        if total_animal_num == 0:
            self.calf_percent = 0
            self.heiferI_percent = 0
            self.heiferII_percent = 0
            self.heiferIII_percent = 0
            self.cow_percent = 0
        else:
            self.calf_percent = self.calf_num / total_animal_num * 100
            self.heiferI_percent = self.heiferI_num / total_animal_num * 100
            self.heiferII_percent = self.heiferII_num / total_animal_num * 100
            self.heiferIII_percent = self.heiferIII_num / total_animal_num * 100
            self.cow_percent = self.cow_num / total_animal_num * 100

        if self.cow_num == 0:
            self.dry_cow_percent = 0
            self.milking_cow_percent = 0
            self.preg_cow_percent = 0
            self.non_preg_cow_percent = 0
        else:
            self.dry_cow_percent = self.dry_cow_num / self.cow_num * 100
            self.milking_cow_percent = self.milking_cow_num / self.cow_num * 100
            self.preg_cow_percent = self.preg_cow_num / self.cow_num * 100
            self.non_preg_cow_percent = self.open_cow_num / self.cow_num * 100

        for parity in self.num_cow_for_parity:
            if self.cow_num == 0:
                self.percent_cow_for_parity[parity] = 0
            else:
                self.percent_cow_for_parity[parity] = \
                    self.num_cow_for_parity[parity] / self.cow_num * 100
        return animals_added, ids_removed, calves_born, calves, heiferIs, \
               heiferIIs, heiferIIIs, cows
    @staticmethod
    def calc_average(num_values, cur_avg, new_value):
        """
        Calcuate the new average given the number of values, the current average, and the new value.

        Args:
            num_values: number of values for the current average
            cur_avg: the current average value
            new_value: the new value to be averaged

        Return:
            new_num_values: the new number of values for the new average
            new_avg: the new average value calculated
        """
        new_num_values = num_values + 1
        new_avg = (cur_avg * num_values + new_value) / new_num_values

        return new_num_values, new_avg

    @staticmethod
    def moving_average(new_value, length_moving, stor_list):
        """
        Calcuate the new average given the number of values, the current average, and the new value.

        Args:
            new_values: the new value to be averaged
            lenth_moving: the length of the moving average period
            stor_list: list where stores the values between averaging period

        Return:
            avg_value: moving average value
        """
        if len(stor_list) == length_moving:
            stor_list = stor_list[1:]+[new_value]
        else: 
            stor_list += [new_value]

        avg_value = sum(stor_list)/length_moving
        
        return avg_value, stor_list
