################################################################################
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
################################################################################
from RUFAS.routines.animal.life_cycle.calf import Calf
from RUFAS.routines.animal.life_cycle.heiferI import HeiferI
from RUFAS.routines.animal.life_cycle.heiferII import HeiferII
from RUFAS.routines.animal.life_cycle.heiferIII import HeiferIII
from RUFAS.routines.animal.life_cycle.cow import Cow
from RUFAS.routines.animal.life_cycle.animal_base import AnimalBase
from RUFAS.routines.animal.life_cycle.animal_initialization import \
    AnimalInitalization
import matplotlib as mpl
from RUFAS.routines.animal.life_cycle import animal_events_constants as c


class LifeCycleManager:
    """
    Manages the life cycles of the animals.
    """
    # statistics
    sold_calves = []
    sold_heifers = []
    culled_heifers = []
    culled_cows = []
    total_culled = 0
    total_new_born = 0
    sold_to_market = 0
    bought_from_market = 0

    # figures
    daily_calf_num = []
    daily_heiferI_num = []
    daily_heiferII_num = []
    daily_heiferIII_num = []
    daily_cow_num = []
    culled_cows_lst = []
    heifer_sold_lst = []
    replacement_bought_lst = []
    milking_cows_lst = []

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
    sold_calf_num = 0
    sold_heifer_num = 0
    bought_heifer_num = 0
    culled_heifer_num = 0
    culled_cow_num = 0

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

    preg_check_num = 0
    GnRH_injection_num = 0
    PGF_injection_num = 0

    open_cow_num = 0
    dry_cow_num = 0
    milking_cow_num = 0
    preg_cow_num = 0
    vwp_cow_num = 0
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

    num_culled_range = 0
    num_heiferII_preg = 0
    num_cow_preg = 0
    num_cow_milking = 0
    num_cow_in_vwp = 0 
    total_replacement_bought = 0
    total_calf_sold = 0
    total_heifer_sold = 0
    cull_reason_stats = {
        c.LOW_PROD_CULL: 0,
        c.LAMENESS_CULL: 0,
        c.INJURY_CULL: 0,
        c.MASTITIS_CULL: 0,
        c.DISEASE_CULL: 0,
        c.UDDER_CULL: 0,
        c.UNKNOWN_CULL: 0
    }
    cull_reason_stats_percent = {
        c.LOW_PROD_CULL: 0,
        c.LAMENESS_CULL: 0,
        c.INJURY_CULL: 0,
        c.MASTITIS_CULL: 0,
        c.DISEASE_CULL: 0,
        c.UDDER_CULL: 0,
        c.UNKNOWN_CULL: 0
    }
    cull_reason_stats_range = {}
    parity_culling_stats_range = {}

    count_21_days = 0
    num_ai_21_days = 0
    num_cow_btw_vwp_preg_21_days = 0
    service_rate_sum_21_days = 0
    num_preg_21_days = 0
    conception_rate_sum_21_days = 0

    avg_service_rate = 0
    avg_conception_rate = 0
    pregnancy_rate = 0
    ai_num = 0
    semen_num = 0

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
                        sim_days=1500):
        """
        Generates a replacement herd to simulate the market, for the herd to get
         replacements. Initializes the herd.

        Args:
            herd_init: boolean - true to populate database with new animals,
                false to use current database
            herd_num: what the number of cows should be maintained at
            calf_num: the number of calves to start the simulation with
            heiferI_num: the number of heiferIs to start the simulation with
            heiferII_num: the number of heiferIIs to start the simulation with
            heiferIII_num: the number of heiferIIIs to start the simulation with
            cow_num: the number of cows to start the simulation with
            replace_num: replacements in the market
            sim_days: simulation length of this herd, to make sure they reach to
                the heiferIII stage

        Returns:
            calves: list of calves for the simulation
            heiferIs: list of heiferIs for the simulation
            heiferIIs: list of heiferIIs for the simulation
            heiferIIIs: list of heiferIIIs for the simulation
            cows: list of cows for the simulation
        """
        self.animal_initializer = AnimalInitalization(self.config['calving_interval'], breed, herd_init)
        if self.config['use_input_calving_interval']:
            self.avg_CI = self.config['calving_interval']
        else:
            self.initialize_db_summary = \
                self.animal_initializer.initialization_db_summary()
            self.avg_CI = self.initialize_db_summary['cow_avg_CI']
        self.herd_num = herd_num

        calves = self.animal_initializer.get_calves(calf_num)
        for calf in calves:
            calf.events.add_event(calf.days_born, 0, c.INIT_HERD)

        heiferIs = self.animal_initializer.get_heiferIs(heiferI_num)
        for heiferI in heiferIs:
            heiferI.events.add_event(heiferI.days_born, 0, c.INIT_HERD)

        heiferIIs = self.animal_initializer.get_heiferIIs(heiferII_num)
        for heiferII in heiferIIs:
            heiferII.events.add_event(heiferII.days_born, 0, c.INIT_HERD)

        heiferIIIs = self.animal_initializer.get_heiferIIIs(heiferIII_num)
        for heiferIII in heiferIIIs:
            heiferIII.events.add_event(heiferIII.days_born, 0, c.INIT_HERD)

        cows = self.animal_initializer.get_cows(cow_num)
        for cow in cows:
            cow.events.add_event(cow.days_born, 0, c.INIT_HERD)

        self.replacement_market = self.animal_initializer.get_replacement_cows(replace_num)
        return calves, heiferIs, heiferIIs, heiferIIIs, cows

    def daily_update(self, date, sim_length, calves, heiferIs, heiferIIs,
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
            sim_length: length of the simulation, days

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

        # record the last days stats
        daily_cow_cull_num = 0
        daily_heifer_culled_num = 0
        daily_heifer_sold = 0
        daily_bought_from_market = 0
        daily_cow_milking = 0
        self.daily_calf_num.append(len(calves))
        self.daily_heiferI_num.append(len(heiferIs))
        self.daily_heiferII_num.append(len(heiferIIs))
        self.daily_heiferIII_num.append(len(heiferIIIs))
        self.daily_cow_num.append(len(cows))

        self.calf_num = 0
        self.heiferI_num = 0
        self.heiferII_num = 0
        self.heiferIII_num = 0
        self.cow_num = 0
        self.sold_calf_num = 0
        self.sold_heifer_num = 0
        self.bought_heifer_num = 0
        self.culled_heifer_num = 0
        self.culled_cow_num = 0
        total_animal_num = 0

        self.preg_check_num = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num = 0
        self.ai_num = 0

        self.daily_milk_production = 0
        self.open_cow_num = 0
        self.preg_cow_num = 0
        self.vwp_cow_num = 0
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

        for parity in self.num_cow_for_parity:
            self.num_cow_for_parity[parity] = 0
            self.percent_cow_for_parity[parity] = 0
            self.avg_age_for_parity[parity] = 0
            self.avg_age_for_calving[parity] = 0
            self.avg_calving_to_preg_time[parity] = 0

        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats[cull_reason] = 0
            self.cull_reason_stats_percent[cull_reason] = 0


        # calf to heiferI
        for index, calf in enumerate(calves):
            wean_day = calf.update(date)
            if wean_day:
                args = calf.get_calf_values()
                args.update({
                    'body_weight_history': calf.body_weight_history,
                    'pen_history': calf.pen_history
                     })
                new_heiferI = HeiferI(args)
                heiferIs.append(new_heiferI)
                del calves[index]
            else:
                self.calf_num += 1
                total_animal_num, self.avg_mature_body_weight = \
                    self._calc_average(total_animal_num,
                    self.avg_mature_body_weight, calf.mature_body_weight)
            # if date == 50:
            #     print(len(calves))
            #     print(calves[0])
            #     return

        # heiferI to heiferII, assign repro programs
        for index, heiferI in enumerate(heiferIs):
            second_stage = heiferI.update(date)
            if second_stage:
                args = heiferI.get_heiferI_values()
                args.update({
                    'body_weight_history': heiferI.body_weight_history,
                    'pen_history': heiferI.pen_history
                     })
                args.update(repro_program=AnimalBase.config['heifer_repro_method'])
                args.update(tai_method_h=AnimalBase.config['heifer_TAI_protocol'])
                args.update(synch_ed_method_h=AnimalBase.config['heifer_synchED_protocol'])
                new_heiferII = HeiferII(args)
                heiferIIs.append(new_heiferII)
                del heiferIs[index]
            else:
                self.heiferI_num += 1
                total_animal_num, self.avg_mature_body_weight = \
                    self._calc_average(total_animal_num,
                    self.avg_mature_body_weight, heiferI.mature_body_weight)
            # if date == 350:
            #     print(len(heiferIs))
            #     print(heiferIs[20])
            #     return

        # heiferII to heiferIII
        for index, heiferII in enumerate(heiferIIs):
            cull_stage, third_stage = heiferII.update(date)
            if cull_stage:
                self.total_culled += 1
                daily_heifer_culled_num += 1
                self.culled_heifer_num, self.avg_heifer_culling_age = \
                    self._calc_average(self.culled_heifer_num,
                    self.avg_heifer_culling_age, heiferII.days_born)
                self.culled_heifers.append(heiferII)
                del heiferIIs[index]
            elif third_stage:
                args = heiferII.get_heiferII_values()
                args.update({
                    'body_weight_history': heiferII.body_weight_history,
                    'pen_history': heiferII.pen_history,
                    'conceptus_weight': heiferII.conceptus_weight
                     })
                new_heiferIII = HeiferIII(args)
                heiferIIIs.append(new_heiferIII)
                del heiferIIs[index]
            else:
                self.heiferII_num += 1
                total_animal_num, self.avg_mature_body_weight = \
                    self._calc_average(total_animal_num,
                    self.avg_mature_body_weight, heiferII.mature_body_weight)
                if heiferII.breeding_to_preg_time != 0:
                    preg_heifer_num, self.avg_breeding_to_preg_time = \
                        self._calc_average(preg_heifer_num,
                        self.avg_breeding_to_preg_time,
                        heiferII.breeding_to_preg_time)
            # if date == 650:
            #     print(len(heiferIIs))
            #     print(heiferIIs[20])
            #     return

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
                    'conceptus_weight': heiferIII.conceptus_weight
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
                total_animal_num, self.avg_mature_body_weight = \
                    self._calc_average(total_animal_num,
                    self.avg_mature_body_weight, heiferIII.mature_body_weight)
            # if date == 850:
            #     print(len(heiferIIIs))
            #     print(heiferIIIs[2])
            #     return

        # if the number of heifers is more than needed for the herd, sell
        # those as replacement
        while len(heiferIIIs) + len(cows) > self.herd_num * 1.03 and len(heiferIIIs) > 0:
            removed = heiferIIIs.pop()
            ids_removed.append(removed.id)
            self.sold_to_market += 1
            self.sold_heifers.append(removed)
            daily_heifer_sold += 1
            self.sold_heifer_num += 1

        # if the number of heifers is less than needed for the herd,
        # buy replacement from the market
        while len(cows) + len(heiferIIIs) + daily_bought_from_market < self.herd_num * 1.01 and \
                date > 1:
            self.replacement_market[0].events.add_event(
                self.replacement_market[0].days_born, date, c.ENTER_HERD)
            self.replacement_market[0].set_p_purchased()
            animals_added.append(self.replacement_market[0])
            self.bought_from_market += 1
            daily_bought_from_market += 1
            self.bought_heifer_num += 1
            del self.replacement_market[0]

        # cow culling action and economic stats
        for index, cow in enumerate(cows):
            _, _, _, culled, new_born = cow.update(date, self.avg_CI)
            # if date == 2000:
            #     print(len(cows))
            #     print(cows[20])
            #     return

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

                self.culled_cows.append(cow)
                self.cull_reason_stats[cow.cull_reason] += 1
                self.total_culled += 1
                daily_cow_cull_num += 1
                self.culled_cow_num, self.avg_cow_culling_age = \
                    self._calc_average(self.culled_cow_num,
                    self.avg_cow_culling_age, cow.days_born)

                # print(len(culled_cows))
                ids_removed.append(cow.id)
                del cows[index]

            else:
                _, self.avg_cow_body_weight = self._calc_average(
                    self.cow_num, self.avg_cow_body_weight, cow.body_weight)
                self.cow_num, self.avg_parity_num = self._calc_average(
                    self.cow_num, self.avg_parity_num, cow.calves)
                total_animal_num, self.avg_mature_body_weight = \
                    self._calc_average(total_animal_num,
                    self.avg_mature_body_weight, cow.mature_body_weight)

                if cow.milking:
                    daily_cow_milking += 1
                    self.daily_milk_production += cow.estimated_daily_milk_produced
                    self.milking_cow_num, self.avg_days_in_milk = \
                        self._calc_average(self.milking_cow_num,
                        self.avg_days_in_milk, cow.days_in_milk)
                else:
                    self.dry_cow_num += 1

                if cow.days_in_milk < self.config['voluntary_waiting_period']:
                    self.vwp_cow_num += 1
                    if not cow.preg:
                        self.open_cow_num += 1

                if cow.preg:
                    self.preg_cow_num, self.avg_days_in_preg = \
                        self._calc_average(self.preg_cow_num,
                        self.avg_days_in_preg, cow.days_in_preg)

                if cow.calves <=3:
                    self.num_cow_for_parity[str(cow.calves)], \
                        self.avg_age_for_parity[str(cow.calves)] = \
                            self._calc_average(
                                self.num_cow_for_parity[str(cow.calves)],
                                self.avg_age_for_parity[str(cow.calves)],
                                cow.days_born)
                    calving_age = cow.events.get_most_recent_date('New birth, start milking')
                    if calving_age != -1:
                        calving_age_available_num[str(cow.calves)], \
                            self.avg_age_for_calving[str(cow.calves)] = \
                                self._calc_average(
                                    calving_age_available_num[str(cow.calves)],
                                    self.avg_age_for_calving[str(cow.calves)],
                                    calving_age)
                    if cow.calving_to_preg_time != 0:
                        calving_to_preg_time_available_num[str(cow.calves)], \
                            self.avg_calving_to_preg_time[str(cow.calves)] = \
                                self._calc_average(
                                    calving_to_preg_time_available_num[str(cow.calves)],
                                    self.avg_calving_to_preg_time[str(cow.calves)],
                                    cow.calving_to_preg_time)
                else:
                    self.num_cow_for_parity['greater_than_3'], \
                        self.avg_age_for_parity['greater_than_3'] = self._calc_average(
                            self.num_cow_for_parity['greater_than_3'],
                            self.avg_age_for_parity['greater_than_3'], cow.days_born)
                    calving_age = cow.events.get_most_recent_date('New birth, start milking')
                    if calving_age != -1:
                        calving_age_available_num['greater_than_3'], \
                            self.avg_age_for_calving['greater_than_3'] = \
                                self._calc_average(
                                    calving_age_available_num['greater_than_3'],
                                    self.avg_age_for_calving['greater_than_3'],
                                    calving_age)
                    if cow.calving_to_preg_time != 0:
                        calving_to_preg_time_available_num['greater_than_3'], \
                            self.avg_calving_to_preg_time['greater_than_3'] = \
                                self._calc_average(
                                    calving_to_preg_time_available_num['greater_than_3'],
                                    self.avg_calving_to_preg_time['greater_than_3'],
                                    cow.calving_to_preg_time)

                if cow.CI != 0:
                    calving_interval_available_num, \
                        self.avg_calving_interval = self._calc_average(
                            calving_interval_available_num,
                            self.avg_calving_interval, cow.CI)

                self.GnRH_injection_num += cow.GnRH_injections
                self.PGF_injection_num += cow.PGF_injections
                self.preg_check_num += cow.preg_diagnoses
                self.semen_num += cow.semen_num
                self.ai_num += cow.AI_times

            # sold calves
            if new_born:
                args = {
                    'id': self.animal_initializer.next_id(),
                    'breed': 'HO',
                    'birth_date': date,
                    'days_born': 0,
                    'p_init': cow.p_gest_for_calf
                }
                # at parturition, the sum of P absorbed for gestation rqmts is
                # subtracted from the animal value. the sum of P absorbed for
                # gestation is equal to the initial animal P value for the calf
                # (A.1G.A.4)
                cow.p_animal = cow.p_animal - cow.p_gest_for_calf + \
                    cow.p_growth + cow.dP_reserves

                new_calf = Calf(args)
                cow.p_gest_for_calf = 0

                if not (new_calf.culled or new_calf.sold):
                    new_calf.events.add_event(
                        new_calf.days_born, date, c.ENTER_HERD)
                    # calves.append(new_calf)
                    self.total_new_born += 1
                    calves_born.append(new_calf)
                if new_calf.sold:
                    self.total_calf_sold += 1
                    self.sold_calf_num += 1
                    self.sold_calves.append(new_calf)

            # calculate reproduction indications
            if date >= sim_length - 21 * self.config["num_21_days_repro"]:
                if cow.ai_day == cow.days_born:
                    self.num_ai_21_days += 1
                if cow.days_in_milk > self.config["voluntary_waiting_period"] and not cow.preg:
                    self.num_cow_btw_vwp_preg_21_days += 1
                if cow.days_in_preg == 1:
                    self.num_preg_21_days += 1

        # calculate service rate and conception rate
        if date >= sim_length - 21 * self.config["num_21_days_repro"]:
            self.count_21_days += 1
            if self.count_21_days % 21 == 0 and self.herd_num > 50:
                self.service_rate_sum_21_days += \
                    float(self.num_ai_21_days) / \
                    float(self.num_cow_btw_vwp_preg_21_days) * 21
                self.conception_rate_sum_21_days += \
                    float(self.num_preg_21_days) / \
                    float(self.num_ai_21_days)
                self.num_ai_21_days = 0
                self.num_cow_btw_vwp_preg_21_days = 0
                self.num_preg_21_days = 0

        # for figures
        self.culled_cows_lst.append(daily_cow_cull_num)
        self.heifer_sold_lst.append(daily_heifer_sold)
        self.replacement_bought_lst.append(daily_bought_from_market)
        self.milking_cows_lst.append(daily_cow_milking)

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
            self.non_preg_cow_percent = (self.open_cow_num + self.vwp_cow_num) / self.cow_num * 100

        for cull_reason in self.cull_reason_stats:
            if self.culled_cow_num != 0:
                self.cull_reason_stats_percent[cull_reason] = \
                    self.cull_reason_stats[cull_reason] / \
                        self.culled_cow_num * 100
        for parity in self.num_cow_for_parity:
            if self.cow_num == 0:
                self.percent_cow_for_parity[parity] = 0
            else:
                self.percent_cow_for_parity[parity] = \
                    self.num_cow_for_parity[parity] / self.cow_num * 100

        self.avg_service_rate = self.service_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        self.avg_conception_rate = self.conception_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        self.pregnancy_rate = self.avg_service_rate * self.avg_conception_rate

        return animals_added, ids_removed, calves_born, calves, heiferIs, \
            heiferIIs, heiferIIIs, cows

    def _calc_average(self, num_values, cur_avg, new_value):
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
