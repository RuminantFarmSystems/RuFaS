'''
RUFAS: Ruminant Farm Systems Model
File name: herd_simulation.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file simulates the whole herd with herd size and simulation length

'''

from collections import Counter
from animal_base import AnimalBase
from calf import Calf
from heiferI import HeiferI
from heiferII import HeiferII
from heiferIII import HeiferIII
from cow import Cow
from config import Config

config = Config()
NUM_21_DAYS = 15


def generate_replacement_herd(max_num, sim_days=1500):
    calves = []
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []
    for _ in range(max_num):
        args = {
            'breed': 'HO',
            'date': 0,
            'days_born': 0
        }
        new_calf = Calf(args)
        if not (new_calf._culled or new_calf._sold):
            calves.append(new_calf)

    for date in range(sim_days):
        for calf in calves:
            wean_day = calf.update()
            if wean_day:
                new_heiferI = HeiferI(calf)
                heiferIs.append(new_heiferI)
                calves.remove(calf)

        for heiferI in heiferIs:
            second_stage = heiferI.update()
            if second_stage:
                args = {
                    'repro_program': 'TAI',
                    'tai_method_h': '5dCG2P',
                    'synch_ed_method_h': '2P'
                }
                new_heiferII = HeiferII(heiferI, args)
                heiferIIs.append(new_heiferII)
                heiferIs.remove(heiferI)

        for heiferII in heiferIIs:
            cull_stage, third_stage = heiferII.update()
            # if date == 900:
            #     print(len(calves))
            #     print(heiferIIs[0])
            #     return
            if cull_stage:
                heiferIIs.remove(heiferII)
            if third_stage:
                new_heiferIII = HeiferIII(heiferII)
                heiferIIIs.append(new_heiferIII)
                heiferIIs.remove(heiferII)

        for heiferIII in heiferIIIs:
            cow_stage = heiferIII.update()
            if cow_stage:
                args = {
                    'repro_program': 'TAI',
                    'presynch_method': 'PreSynch',
                    'tai_method_c': 'OvSynch 56',
                    'resynch_method': 'TAIafterPD'
                }
                new_cow = Cow(heiferIII, args)
                cows.append(new_cow)
                heiferIIIs.remove(heiferIII)

    return cows

def start_simulation(herd_num, sim_length, replacement_market):
    calves = []
    start_date = 0
    # initialize calves
    for _ in range(herd_num):
        args = {
            'breed': 'HO',
            'date': 0,
            'days_born': 0
        }
        new_calf = Calf(args)
        if not (new_calf._culled or new_calf._sold):
            calves.append(new_calf)

    # stats
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []
    sold_calves = []
    sold_heifers = []
    culled_heifers = []
    culled_cows = []
    total_culled = 0
    total_new_born = 0
    bought_from_market = 0

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
    total_replacement_cost = 0
    total_slaughter_value = 0
    total_calf_value = 0
    total_heifer_value = 0
    total_milk_income = 0
    cull_reason_stats = {}
    cull_reason_stats_range = {}
    parity_culling_stats_range = {}

    count_21_days = 0
    num_ai_21_days = 0
    num_cow_btw_vwp_preg_21_days = 0
    service_rate_sum_21_days = 0
    num_preg_21_days = 0
    num_ai_21_days = 0
    conception_rate_sum_21_days = 0



    for date in range(sim_length):
        record_econ_stats = False
        if sim_length - date <= config.econ_indicator_range:
            record_econ_stats = True

        for calf in calves:
            wean_day = calf.update()
            if wean_day:
                new_heiferI = HeiferI(calf)
                heiferIs.append(new_heiferI)
                calves.remove(calf)

        for heiferI in heiferIs:
            second_stage = heiferI.update()
            if second_stage:
                args = {
                    'repro_program': 'TAI',
                    'tai_method_h': '5dCG2P',
                    'synch_ed_method_h': '2P'
                }
                new_heiferII = HeiferII(heiferI, args)
                heiferIIs.append(new_heiferII)
                heiferIs.remove(heiferI)

        for heiferII in heiferIIs:
            cull_stage, third_stage = heiferII.update()
            # if date == 700:
            #     print(len(calves))
            #     print(heiferIIs[0])
            #     return
            if cull_stage:
                total_culled += 1
                culled_heifers.append(heiferII)
                heiferIIs.remove(heiferII)
            if third_stage:
                new_heiferIII = HeiferIII(heiferII)
                heiferIIIs.append(new_heiferIII)
                heiferIIs.remove(heiferII)

        for heiferIII in heiferIIIs:
            cow_stage = heiferIII.update()
            if cow_stage:
                args = {
                    'repro_program': 'TAI',
                    'presynch_method': 'PreSynch',
                    'tai_method_c': 'OvSynch 56',
                    'resynch_method': 'TAIafterPD'
                }
                new_cow = Cow(heiferIII, args)
                cows.append(new_cow)
                heiferIIIs.remove(heiferIII)

        while len(heiferIIIs) > herd_num - len(cows):
            heiferIIIs.pop(0)
            if record_econ_stats:
                total_heifer_value += config.heifer_sell_price

        while len(cows) + len(heiferIIIs) < herd_num and date > 1000:
            cows.append(replacement_market[0])
            bought_from_market += 1
            del replacement_market[0]
            if record_econ_stats:
                total_replacement_cost += config.heifer_buy_price

        for cow in cows:
            _, _, _, _, culled, new_born = cow.update(record_econ_stats)
            # if date == 1500:
            #     #print(len(calves))
            #     print(cows[10])
            #     return
            if culled:
                repro_cost, semen_cost, AI_cost, preg_check_cost, feed_cost, fixed_cost, milk_income, slaughter_value = cow.get_economy_stats()
                if record_econ_stats:
                    total_slaughter_value += slaughter_value
                    num_culled_range += 1
                    if cow._cull_reason in cull_reason_stats_range:
                        cull_reason_stats_range[cow._cull_reason] += 1
                    else:
                        cull_reason_stats_range[cow._cull_reason] = 1
                    parity = cow._calves if cow._calves <= 3 else '4+'
                    if cow._calves in parity_culling_stats_range:
                        parity_culling_stats_range[parity] += 1
                    else:
                        parity_culling_stats_range[parity] = 1

                if cow._cull_reason in cull_reason_stats:
                    cull_reason_stats[cow._cull_reason] += 1
                else:
                    cull_reason_stats[cow._cull_reason] = 1
                total_culled += 1
                cows.remove(cow)
            if new_born:
                args = {
                    'breed': 'HO',
                    'date': 0,
                    'days_born': 0
                }
                new_calf = Calf(args)
                if not (new_calf._culled or new_calf._sold):
                    calves.append(new_calf)
                    total_new_born += 1
                if new_calf._sold:
                    total_calf_value += config.calf_price
            if date >= sim_length - 21 * NUM_21_DAYS:
                if cow._ai_day == cow._days_born:
                    num_ai_21_days += 1
                if cow._days_in_milk > config.vwp and not cow._preg:
                    num_cow_btw_vwp_preg_21_days += 1
                if cow._days_in_preg == 1:
                    num_preg_21_days += 1

        if date >= sim_length - 21 * NUM_21_DAYS:
            count_21_days += 1
            if count_21_days % 21 == 0:
                service_rate_sum_21_days += float(num_ai_21_days) / float(num_cow_btw_vwp_preg_21_days)
                conception_rate_sum_21_days += float(num_preg_21_days) / float(num_ai_21_days)
                num_ai_21_days = 0
                num_cow_btw_vwp_preg_21_days = 0
                num_preg_21_days = 0


    # count stats
    for heiferII in heiferIIs:
        if heiferII._preg:
            num_heiferII_preg += 1
    for cow in cows:
        if cow._preg:
            num_cow_preg += 1
        if cow._milking:
            num_cow_milking += 1
        if cow._days_in_milk < config.vwp:
            num_cow_in_vwp += 1

        # calculate economy date
        repro_cost, semen_cost, AI_cost, preg_check_cost, feed_cost, fixed_cost, milk_income, slaughter_value = cow.get_economy_stats()
        total_breeding_cost += repro_cost
        total_semen_cost += semen_cost
        total_ai_cost += AI_cost
        total_preg_check_cost += preg_check_cost
        total_feed_cost += feed_cost
        total_fixed_cost += fixed_cost
        total_milk_income += milk_income

    parity_lst = [cow._calves if cow._calves <= 3 else '4+' for cow in cows ]
    parity_count_tuple = Counter(parity_lst)
    avg_service_rate = service_rate_sum_21_days / float(NUM_21_DAYS) * 21.0
    avg_conception_rate = conception_rate_sum_21_days / float(NUM_21_DAYS)
    pregnancy_rate = avg_service_rate * avg_conception_rate
    print("Total calves:\t\t\t{}".format(len(calves)))
    print("Total heiferI:\t\t\t{}".format(len(heiferIs)))
    print("Total heiferII:\t\t\t{}".format(len(heiferIIs)))
    print("Total heiferIII:\t\t{}".format(len(heiferIIIs)))
    print("Total cows:\t\t\t{}".format(len(cows)))
    print("Total female new borns: \t{}".format(total_new_born))
    print("Total bought from market: \t{}".format(bought_from_market))
    print("Total culled:\t\t\t{}".format(total_culled))
    for cull_reason, count in cull_reason_stats.items():
        print("{} => {}".format(cull_reason, count))

    print("\n=================== Last {} days economy stats ===================\n".format(config.econ_indicator_range))
    print("Total heiferII pregnant:\t{}".format(num_heiferII_preg))
    print("Total cows pregnant:\t\t{}".format(num_cow_preg))
    print("Total cows milking:\t\t{}".format(num_cow_milking))
    print("Total cows in vwp:\t\t{}".format(num_cow_in_vwp))
    print("Total feed cost:\t\t{0:.2f}".format(total_feed_cost))
    print("Total fixed cost:\t\t{0:.2f}".format(total_fixed_cost))
    print("Total breeding cost:\t\t{0:.2f}".format(total_breeding_cost))
    print("Total semen cost:\t\t{0:.2f}".format(total_semen_cost))
    print("Total ai cost:\t\t\t{0:.2f}".format(total_ai_cost))
    print("Total preg check cost:\t\t{0:.2f}".format(total_preg_check_cost))
    print("Total replacement cost:\t\t{0:.2f}".format(total_replacement_cost))
    print("Total slaughter income:\t\t{0:.2f}".format(total_slaughter_value))
    print("Total calf sold income:\t\t{0:.2f}".format(total_calf_value))
    print("Total heifer sold income:\t{0:.2f}".format(total_heifer_value))
    print("Total milk income:\t\t{0:.2f}".format(total_milk_income))
    print("Total cows culled:\t\t{}".format(num_culled_range))
    print("SR%: {}%".format(avg_service_rate * 100.0))
    print("CR%: {}%".format(avg_conception_rate * 100.0))
    print("PR%: {}%".format(pregnancy_rate * 100.0))
    print("Culling rate: {}%".format(float(num_culled_range) / float(len(cows)) * 100))
    for cull_reason, count in cull_reason_stats_range.items():
        print("{} => {}".format(cull_reason, count))
    for parity, count in parity_count_tuple.items():
        print("Parity {}: {}".format(parity, count))
    for parity, count in parity_culling_stats_range.items():
        print("Parity {} total culls: {}".format(parity, count))

if __name__ == "__main__":
    replacement_market = generate_replacement_herd(3000)
    start_simulation(100, 3000, replacement_market)
