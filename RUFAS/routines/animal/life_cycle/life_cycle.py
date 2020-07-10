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
from RUFAS.routines.animal.life_cycle.animal_initialization import AnimalInitalization
from collections import Counter
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.use('TkAgg')


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
    sold_heifer_num = 0
    bought_heifer_num = 0
    culled_cow_num = 0

    parity_num = {
        '1': 0,
        '2': 0,
        '3': 0,
        '>3': 0
    }
    parity_percent = {
        '1': 0,
        '2': 0,
        '3': 0,
        '>3': 0
    }

    preg_check_num = 0
    GnRH_injection_num = 0
    PGF_injection_num = 0

    open_cow_num = 0
    dry_cow_num = 0
    milking_cow_num = 0
    preg_cow_num = 0
    daily_milk_production = 0
    avg_days_in_milk = 0
    avg_days_in_preg = 0

    num_culled_range = 0
    num_heiferII_preg = 0
    num_cow_preg = 0
    num_cow_milking = 0
    num_cow_in_vwp = 0
    total_feed_cost = 0
    total_fixed_cost = 0
    total_breeding_cost = 0
    total_semen_cost = 0
    total_ai_cost = 0
    total_preg_check_cost = 0
    total_replacement_bought = 0
    total_replacement_cost = 0
    avg_slaughter_value = 0
    total_slaughter_value = 0
    total_calf_sold = 0
    total_calf_value = 0
    total_heifer_sold = 0
    total_heifer_value = 0
    total_milk_income = 0
    cull_reason_stats = {
        'Low production': 0,
        'Lameness': 0,
        'Injury': 0,
        'Mastitis': 0,
        'Disease': 0,
        'Udder': 0,
        'Unknown': 0
    }
    cull_reason_stats_percent = {
        'Low production': 0,
        'Lameness': 0,
        'Injury': 0,
        'Mastitis': 0,
        'Disease': 0,
        'Udder': 0,
        'Unknown': 0
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

    def initialize_herd(self, herd_num, calf_num, heiferI_num, heiferII_num,
                        heiferIII_num, cow_num, replace_num, sim_days=1500):
        """
        Generates a replacement herd to simulate the market, for the herd to get
         replacements. Initializes the herd.

        Args:
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
        self.animal_initializer = AnimalInitalization(False)
        self.herd_num = herd_num
        calves = self.animal_initializer.get_calves(calf_num)
        heiferIs = self.animal_initializer.get_heiferIs(heiferI_num)
        heiferIIs = self.animal_initializer.get_heiferIIs(heiferII_num)
        heiferIIIs = self.animal_initializer.get_heiferIIIs(heiferIII_num)
        cows = self.animal_initializer.get_cows(cow_num)
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
        daily_heifer_sold = 0
        daily_bought_from_market = 0
        daily_cow_milking = 0
        total_days_in_milk = 0
        total_days_in_preg = 0
        self.daily_calf_num.append(len(calves))
        self.daily_heiferI_num.append(len(heiferIs))
        self.daily_heiferII_num.append(len(heiferIIs))
        self.daily_heiferIII_num.append(len(heiferIIIs))
        self.daily_cow_num.append(len(cows))

        self.open_cow_num = 0
        self.dry_cow_num = 0
        self.milking_cow_num = 0
        self.preg_cow_num = 0
        self.num_cow_in_vwp = 0
        self.daily_milk_production = 0
        self.preg_check_num = 0
        self.GnRH_injection_num = 0
        self.PGF_injection_num = 0
        self.ai_num = 0

        self.calf_num = len(calves)
        self.heiferI_num = len(heiferIs)
        self.heiferII_num = len(heiferIIs)
        self.heiferIII_num = len(heiferIIIs)
        self.cow_num = len(cows)

        total_aniaml_num = self.calf_num + self.heiferI_num + self.heiferII_num + self.heiferIII_num + self.cow_num
        self.calf_percent = self.calf_num / total_aniaml_num * 100
        self.heiferI_percent = self.heiferI_num / total_aniaml_num * 100
        self.heiferII_percent = self.heiferII_num / total_aniaml_num * 100
        self.heiferIII_percent = self.heiferIII_num / total_aniaml_num * 100
        self.cow_percent = self.cow_num / total_aniaml_num * 100

        for parity in self.parity_num:
            self.parity_num[parity] = 0

        for cull_reason in self.cull_reason_stats:
            self.cull_reason_stats[cull_reason] = 0

        record_econ_stats = False
        if sim_length - date <= self.config["econ_indicator_range"]:
            record_econ_stats = True

        # calf to heiferI
        for index, calf in enumerate(calves):
            wean_day = calf.update(date)
            if wean_day:
                args = calf.get_calf_values()
                new_heiferI = HeiferI(args)
                heiferIs.append(new_heiferI)
                del calves[index]
            # if date == 50:
            #     print(len(calves))
            #     print(calves[0])
            #     return

        # heiferI to heiferII, assign repro programs
        for index, heiferI in enumerate(heiferIs):
            second_stage = heiferI.update(date)
            if second_stage:
                args = heiferI.get_heiferI_values()
                args.update(repro_program = 'TAI')
                args.update(tai_method_h = '5dCG2P')
                args.update(synch_ed_method_h = '2P')
                new_heiferII = HeiferII(args)
                heiferIIs.append(new_heiferII)
                del heiferIs[index]
            # if date == 350:
            #     print(len(heiferIs))
            #     print(heiferIs[20])
            #     return

        # heiferII to heiferIII
        for index, heiferII in enumerate(heiferIIs):
            cull_stage, third_stage = heiferII.update(date)
            if cull_stage:
                self.total_culled += 1
                self.culled_heifers.append(heiferII)
                del heiferIIs[index]
            if third_stage:
                args = args = heiferII.get_heiferII_values()
                new_heiferIII = HeiferIII(args)
                heiferIIIs.append(new_heiferIII)
                del heiferIIs[index]
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
                cow_stage = heiferIII.update(record_econ_stats, date)

            if cow_stage:
                args = heiferIII.get_heiferIII_values()
                args.update(repro_program = 'TAI')
                args.update(presynch_method = 'PreSynch')
                args.update(tai_method_c = 'OvSynch 56')
                args.update(resynch_method = 'TAIafterPD')
                new_cow = Cow(args)
                cows.append(new_cow)
                del heiferIIIs[index]
            # if date == 850:
            #     print(len(heiferIIIs))
            #     print(heiferIIIs[2])
            #     return

        # if the number of heifers is more than needed for the herd, sell
        # those as replacement
        while len(heiferIIIs) + len(cows) > self.herd_num * 1.03:
            removed = heiferIIIs.pop()
            ids_removed.append(removed.id)
            self.sold_to_market += 1
            self.sold_heifers.append(removed)
            daily_heifer_sold += 1
            if record_econ_stats:
                self.total_heifer_sold += 1
                self.total_heifer_value += self.config["heifer_sell_price"]

        # if the number of heifers is less than needed for the herd,
        # buy replacement from the market
        while len(cows) + len(heiferIIIs) + daily_bought_from_market < self.herd_num * 1.01 and \
                date > 1:
            self.replacement_market[0].events.add_event(
                self.replacement_market[0].days_born, date, 'Entered Herd')
            self.replacement_market[0].set_p_purchased()
            animals_added.append(self.replacement_market[0])
            self.bought_from_market += 1
            daily_bought_from_market += 1
            del self.replacement_market[0]
            if record_econ_stats:
                self.total_replacement_bought += 1
                self.total_replacement_cost += self.config["heifer_buy_price"]

        # cow culling action and economic stats
        for index, cow in enumerate(cows):
            _, _, _, culled, new_born = cow.update(record_econ_stats, date)
            # if date == 2000:
            #     print(len(cows))
            #     print(cows[20])
            #     return

            # culled cows, calculate slaughter value and record culling reasons
            if cow.calves == 0:
                print('this cow has 0 calves')

            if culled:
                repro_cost, semen_cost, AI_cost, preg_check_cost, feed_cost, \
                    fixed_cost, milk_income, slaughter_value = \
                    cow.get_economy_stats()
                if record_econ_stats:
                    self.total_slaughter_value += slaughter_value
                    self.num_culled_range += 1
                    self.avg_slaughter_value = \
                        self.total_slaughter_value / self.num_culled_range
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
                if cow.cull_reason in self.cull_reason_stats:
                    self.cull_reason_stats[cow.cull_reason] += 1
                    self.cull_reason_stats_percent[cow.cull_reason] = \
                        self.cull_reason_stats[cow.cull_reason] / len(self.culled_cows)
                else:
                    self.cull_reason_stats[cow.cull_reason] = 1
                    self.cull_reason_stats_percent[cow.cull_reason] = 1 / len(self.culled_cows)
                self.total_culled += 1
                daily_cow_cull_num += 1

                # print(len(culled_cows))
                ids_removed.append(cow.id)
                del cows[index]

            # calculate income from sold calves
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
                        new_calf.days_born, date, 'Entered Herd')
                    # calves.append(new_calf)
                    self.total_new_born += 1
                    calves_born.append(new_calf)
                if new_calf.sold:
                    self.total_calf_sold += 1
                    self.total_calf_value += self.config["calf_price"]
                    self.sold_calves.append(new_calf)

            # calculate reproduction indications
            if date >= sim_length - 21 * self.config["num_21_days_repro"]:
                if cow.ai_day == cow.days_born:
                    self.num_ai_21_days += 1
                if cow.days_in_milk > self.config["voluntary_waiting_period"] and not cow.preg:
                    self.num_cow_btw_vwp_preg_21_days += 1
                if cow.days_in_preg == 1:
                    self.num_preg_21_days += 1

            if cow.milking:
                self.milking_cow_num += 1
                daily_cow_milking += 1
                self.daily_milk_production += cow.estimated_daily_milk_produced
                total_days_in_milk += cow.days_in_milk
            else:
                self.dry_cow_num += 1

            if cow.days_in_milk < self.config['voluntary_waiting_period']:
                self.num_cow_in_vwp += 1
                if not cow.preg:
                    self.open_cow_num += 1

            if cow.preg:
                self.preg_cow_num += 1
                total_days_in_preg += cow.days_in_preg

            if cow.calves <=3:
                self.parity_num[str(cow.calves)] += 1
                self.parity_percent[str(cow.calves)] = self.parity_num[str(cow.calves)] / self.cow_num * 100
            else:
                self.parity_num['>3'] += 1
                self.parity_percent['>3'] = self.parity_num['>3'] / self.cow_num * 100
                
            self.GnRH_injection_num += cow.GnRH_injections
            self.PGF_injection_num += cow.PGF_injections
            self.preg_check_num += cow.preg_diagnoses
            self.ai_num += cow.AI_times

        # calculate service rate and conception rate
        if date >= sim_length - 21 * self.config["num_21_days_repro"]:
            self.count_21_days += 1
            if self.count_21_days % 21 == 0:
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

        self.sold_heifer_num = daily_heifer_sold
        self.bought_heifer_num = daily_bought_from_market
        self.culled_cow_num = daily_cow_cull_num
        if self.milking_cow_num == 0:
            self.avg_days_in_milk = 0
        else:
            self.avg_days_in_milk = total_days_in_milk / self.milking_cow_num
        if self.preg_cow_num == 0:
            self.avg_days_in_preg = 0
        else:
            self.avg_days_in_preg = total_days_in_preg / self.preg_cow_num

        self.avg_service_rate = self.service_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        self.avg_conception_rate = self.conception_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        self.pregnancy_rate = self.avg_service_rate * self.avg_conception_rate

        return animals_added, ids_removed, calves_born, calves, heiferIs, \
            heiferIIs, heiferIIIs, cows

    def output_end_stats(self, sim_length, calves, heiferIs, heiferIIs,
                         heiferIIIs, cows):
        """
        End of simulation statistics.

        Args:
            cows: list of Cow objects to be updated
            heiferIIIs: list of HeiferIII objects to be updated
            heiferIIs: list of HeiferII objects to be updated
            heiferIs: list of HeiferI objects to be updated
            calves: list of Calf objects to be updated
            sim_length: simulation length, d
        """
        income_over_feed_cost = 0
        net_return = 0
        avg_milk_income = 0
        avg_feed_cost = 0
        avg_fixed_cost = 0
        avg_repro_cost = 0

        # find avg of self.milking_cows_lst
        for daily_val in self.milking_cows_lst:
            self.avg_daily_cow_milking += daily_val
        self.avg_daily_cow_milking /= len(self.milking_cows_lst)

        # count stats
        for heiferII in heiferIIs:
            if heiferII.preg:
                self.num_heiferII_preg += 1
        for cow in cows:
            if cow.preg:
                self.num_cow_preg += 1
            if cow.milking:
                self.num_cow_milking += 1
            if cow.days_in_milk < self.config['voluntary_waiting_period']:
                self.num_cow_in_vwp += 1

            # calculate economy date
            repro_cost, semen_cost, AI_cost, preg_check_cost, feed_cost, \
                fixed_cost, milk_income, \
                slaughter_value = cow.get_economy_stats()
            self.total_breeding_cost += repro_cost
            self.total_semen_cost += semen_cost
            self.total_ai_cost += AI_cost
            self.total_preg_check_cost += preg_check_cost
            total_repro_cost = self.total_breeding_cost + \
                self.total_semen_cost + \
                self.total_ai_cost + \
                self.total_preg_check_cost
            avg_repro_cost = total_repro_cost/365/1000
            self.total_feed_cost += feed_cost
            avg_feed_cost = self.total_feed_cost/365/self.avg_daily_cow_milking
            self.total_fixed_cost += fixed_cost
            avg_fixed_cost = self.total_fixed_cost/365/1000
            self.total_milk_income += milk_income
            avg_milk_income = \
                self.total_milk_income/365/self.avg_daily_cow_milking
            income_over_feed_cost = self.total_milk_income + \
                self.total_slaughter_value + \
                self.total_heifer_value + \
                self.total_calf_value - \
                self.total_feed_cost
            net_return = income_over_feed_cost - \
                self.total_replacement_cost - \
                self.total_fixed_cost

        parity_lst = [cow.calves
                      if cow.calves <= 2 else '3+'
                      for cow in cows]
        parity_count_tuple = Counter(parity_lst)
        avg_service_rate = self.service_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        avg_conception_rate = self.conception_rate_sum_21_days / \
            float(self.config["num_21_days_repro"])
        pregnancy_rate = avg_service_rate * avg_conception_rate

        print("\n=================== Herd structure at the end of the "
              "simulation ===================\n".format(
                self.config["econ_indicator_range"]))
        print("Total calves:\t\t\t{}".format(len(calves)))
        print("Total heiferI:\t\t\t{}".format(len(heiferIs)))
        print("Total heiferII:\t\t\t{}".format(len(heiferIIs)))
        print("Total heiferIII:\t\t{}".format(len(heiferIIIs)))
        print("Total cows:\t\t\t{}".format(len(cows)))
        print("Total heiferII pregnant:\t{}".format(self.num_heiferII_preg))
        print("Total cows pregnant:\t\t{}".format(self.num_cow_preg))
        print("Total cows milking:\t\t{}".format(self.num_cow_milking))
        for parity, count in parity_count_tuple.items():
            print("Parity {}:\t\t\t {}".format(parity, count))
        print("Total cows in vwp:\t\t{}".format(self.num_cow_in_vwp))

        print("\n=================== Last {} days economy stats "
              "===================\n".format(
                self.config["econ_indicator_range"]))
        print("Feed cost:\t\t\t{0:.2f} $/cow/day".format(avg_feed_cost))
        print("Fixed cost:\t\t\t{0:.2f} $/cow/day".format(avg_fixed_cost))
        print("Repro cost:\t\t\t{0:.2f} $/cow/day".format(avg_repro_cost))
        # print("Total breeding cost:\t\t{0:.2f}
        # $".format(self.total_breeding_cost))
        # print("Total semen cost:\t\t{0:.2f} $".format(self.total_semen_cost))
        # print("Total ai cost:\t\t\t{0:.2f} $".format(self.total_ai_cost))
        # print("Total preg check cost:\t\t{0:.2f}
        # $".format(self.total_preg_check_cost))
        print("Milk income:\t\t\t{0:.2f} $/cow/day".format(avg_milk_income))
        print("Total replacement bought:"
              "\t{0:.2f}".format(self.total_replacement_bought))
        print("Total replacement cost:\t\t{0:.2f} "
              "$".format(self.total_replacement_cost))
        print("Total replacement sold:"
              "\t\t{0:.2f}".format(self.total_heifer_sold))
        print("Total heifer sold income:\t{0:.2f} "
              "$".format(self.total_heifer_value))
        print("Total calf sold:\t\t{0:.2f}".format(self.total_calf_sold))
        print("Total calf sold income:\t\t{0:.2f} "
              "$".format(self.total_calf_value))
        print("Total slaughter income:\t\t{0:.2f} "
              "$".format(self.total_slaughter_value))
        print("Average slaughter income:\t{0:.2f} "
              "$".format(self.avg_slaughter_value))
        print("IOFC: \t\t\t\t{0:.2f} $".format(income_over_feed_cost))
        print("Net return: \t\t\t{0:.2f} $".format(net_return))

        print("SR%: \t\t\t\t{0:.2f}%".format(avg_service_rate * 100.0))
        print("CR%: \t\t\t\t{0:.2f}%".format(avg_conception_rate * 100.0))
        print("PR%: \t\t\t\t{0:.2f}%".format(pregnancy_rate * 100.0))
        print("Total cows culled:\t\t{}".format(self.num_culled_range))
        print("Culling rate: \t\t\t{0:.2f}%".format(float(self.num_culled_range)
                                                    / float(len(cows))
                                                    * 100))
        for cull_reason, count in self.cull_reason_stats_range.items():
            print("{} => {}".format(cull_reason, count))
        # for parity, count in self.parity_culling_stats_range.items():
        #     print("Parity {} total culls: {}".format(parity, count))

        self.draw_stat(sim_length)
        # draw curves for a cow
        print(cows[0])
        cows[0].draw_curves()

        print(cows[20])
        cows[20].draw_curves()

        print(cows[150])
        cows[150].draw_curves()

    def draw_stat(self, sim_length):
        """
        Plots the ending statistics of the simulation.

        Args:
            sim_length: simulation length
        """
        fig = plt.figure()
        x = [date for date in range(sim_length)]

        ax1 = fig.add_subplot(521)
        ax1.scatter(x, self.daily_calf_num, s=1)
        ax1.spines['right'].set_visible(False)
        ax1.spines['top'].set_visible(False)
        ax1.set_title("Number of calves each day")

        ax2 = fig.add_subplot(522)
        ax2.scatter(x, self.daily_heiferI_num, s=1)
        ax2.spines['right'].set_visible(False)
        ax2.spines['top'].set_visible(False)
        ax2.set_title("Number of heiferIs each day")

        ax3 = fig.add_subplot(523)
        ax3.scatter(x, self.daily_heiferII_num, s=1)
        ax3.spines['right'].set_visible(False)
        ax3.spines['top'].set_visible(False)
        ax3.set_title("Number of heiferIIs each day")

        ax4 = fig.add_subplot(524)
        ax4.scatter(x, self.daily_heiferIII_num, s=1)
        ax4.spines['right'].set_visible(False)
        ax4.spines['top'].set_visible(False)
        ax4.set_title("Number of heiferIIIs each day")

        ax5 = fig.add_subplot(525)
        ax5.scatter(x, self.daily_cow_num, s=1)
        ax5.spines['right'].set_visible(False)
        ax5.spines['top'].set_visible(False)
        ax5.set_title("Number of cows each day")

        ax6 = fig.add_subplot(526)
        ax6.scatter(x, self.culled_cows_lst, s=1)
        ax6.spines['right'].set_visible(False)
        ax6.spines['top'].set_visible(False)
        ax6.set_title("Number of culled cows each day")

        ax7 = fig.add_subplot(527)
        ax7.scatter(x, self.heifer_sold_lst, s=1)
        ax7.spines['right'].set_visible(False)
        ax7.spines['top'].set_visible(False)
        ax7.set_title("Number of sold heifers each day")

        ax8 = fig.add_subplot(528)
        ax8.scatter(x, self.replacement_bought_lst, s=1)
        ax8.spines['right'].set_visible(False)
        ax8.spines['top'].set_visible(False)
        ax8.set_title("Number of bought heifers each day")

        # ax9 = fig.add_subplot(529)
        # ax9.scatter(x, self.milking_cows_lst, s=1)
        # ax9.spines['right'].set_visible(False)
        # ax9.spines['top'].set_visible(False)
        # ax9.set_title("Number of milking cows each day")

        plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.4)
        plt.show()
