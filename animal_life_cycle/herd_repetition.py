#! ./env/bin/python3
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
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt

config = Config()
NUM_21_DAYS = 15
REPETITIONS = 5

'''
		Description:
			generate a replacement herd to simulate the market, for the herd to get replacements
		Input:
			max_num: the max number of this replacement herd
            sim_days: simulation length of this herd, to make sure they reach to the heiferIII stage
		Output:
			cows: ready to enter the herd
	'''
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

'''
		Description:
			the simulation updates
		Input:
			herd_num: the lactating and dry herd number
            sim_length: the length of the main simulation
            replace_market: call the replacement_market to have the extra heiferIIIs
		Output:
	'''
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

    # stats init
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []
    sold_calves = []
    sold_heifers = []
    culled_heifers = []
    culled_cows = []
    #total_estimated_milk_production = []
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
    total_replacement_bought = 0
    total_replacement_cost = 0
    avg_slaughter_value = 0
    total_slaughter_value = 0
    total_calf_sold = 0
    total_calf_value = 0
    total_heifer_sold = 0
    total_heifer_value = 0
    total_milk_income = 0
    cull_reason_stats = {}
    cull_reason_stats_range = {}
    parity_culling_stats_range = {}

    count_culled_replace = 0

    count_21_days = 0
    num_ai_21_days = 0
    num_cow_btw_vwp_preg_21_days = 0
    service_rate_sum_21_days = 0
    num_preg_21_days = 0
    num_ai_21_days = 0
    conception_rate_sum_21_days = 0


# record the last days stats
    for date in range(sim_length):
        record_econ_stats = False
        if sim_length - date <= config.econ_indicator_range:
            record_econ_stats = True

# calf to heiferI
        for calf in calves:
            wean_day = calf.update()
            if wean_day:
                new_heiferI = HeiferI(calf)
                heiferIs.append(new_heiferI)
                calves.remove(calf)
            if date == 1:
                print(len(calves))
                print(calves[0])
                return

# heiferI to heiferII, assign repro programs
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
            # if date == 350:
            #     print(len(heiferIs))
            #     print(heiferIs[20])
            #     return

# heiferII to heiferIII
        for heiferII in heiferIIs:
            cull_stage, third_stage = heiferII.update()
            if cull_stage:
                total_culled += 1
                culled_heifers.append(heiferII)
                heiferIIs.remove(heiferII)
            if third_stage:
                new_heiferIII = HeiferIII(heiferII)
                heiferIIIs.append(new_heiferIII)
                heiferIIs.remove(heiferII)
            # if date == 650:
            #     print(len(heiferIIs))
            #     print(heiferIIs[20])
            #     return

# heiferIII to cow, assign repro programs
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
            # if date == 850:
            #     print(len(heiferIIIs))
            #     print(heiferIIIs[2])
            #     return

# if the number of heifers is more than needed for the herd, sell those as replacement
        while len(heiferIIIs) > count_culled_replace:
            heiferIIIs.pop(0)
            if record_econ_stats:
                total_heifer_sold += 1
                total_heifer_value += config.heifer_sell_price

# if the number of heifers is less than needed for the herd, buy replacement from the market
        while len(cows) + len(culled_cows) < herd_num and date > 1000:
            cows.append(replacement_market[0])
            bought_from_market += 1
            del replacement_market[0]
            if record_econ_stats:
                total_replacement_bought += 1
                total_replacement_cost += config.heifer_buy_price

# cow culling action and economic stats
        for cow in cows:
            _, _, _, _, culled, new_born = cow.update(record_econ_stats)
            # if date == 2000:
            #     print(len(cows))
            #     print(cows[20])
            #     print(cows[30])
            #     return

            # culled cows, caculate slaughter value and record culling reasons
            if culled:
                repro_cost, semen_cost, AI_cost, preg_check_cost, feed_cost, fixed_cost, milk_income, slaughter_value = cow.get_economy_stats()
                if record_econ_stats:
                    total_slaughter_value += slaughter_value
                    num_culled_range += 1
                    avg_slaughter_value = total_slaughter_value/num_culled_range
                    if cow._cull_reason in cull_reason_stats_range:
                        cull_reason_stats_range[cow._cull_reason] += 1
                    else:
                        cull_reason_stats_range[cow._cull_reason] = 1
                    parity = cow._calves if cow._calves <= 3 else '4+'
                    if cow._calves in parity_culling_stats_range:
                        parity_culling_stats_range[parity] += 1
                    else:
                        parity_culling_stats_range[parity] = 1

                if date >= sim_length - config.replacement_day:
                    count_culled_replace += 1


                if cow._cull_reason in cull_reason_stats:
                    cull_reason_stats[cow._cull_reason] += 1
                else:
                    cull_reason_stats[cow._cull_reason] = 1
                total_culled += 1
                #culled_cows.append(total_culled)
                cows.remove(cow)
            # caculate income from sold calves
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
                    total_calf_sold += 1
                    total_calf_value += config.calf_price

            # caculate reproduction indications
            if date >= sim_length - 21 * NUM_21_DAYS:
                if cow._ai_day == cow._days_born:
                    num_ai_21_days += 1
                if cow._days_in_milk > config.vwp and not cow._preg:
                    num_cow_btw_vwp_preg_21_days += 1
                if cow._days_in_preg == 1:
                    num_preg_21_days += 1

        #caculate service rate and conception rate
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
        total_repro_cost = total_breeding_cost + total_semen_cost + total_ai_cost + total_preg_check_cost
        avg_repro_cost = total_repro_cost/365/1000
        total_feed_cost += feed_cost
        avg_feed_cost = total_feed_cost/365/1000
        total_fixed_cost += fixed_cost
        avg_fixed_cost = total_fixed_cost/365/1000
        total_milk_income += milk_income
        avg_milk_income = total_milk_income/365/1000
        income_over_feed_cost = avg_milk_income - avg_feed_cost
        net_return = total_milk_income + total_slaughter_value + total_heifer_value + total_calf_value - total_feed_cost - total_replacement_cost - total_fixed_cost

    parity_lst = [cow._calves if cow._calves <= 3 else '4+' for cow in cows ]
    parity_count_tuple = Counter(parity_lst)
    avg_service_rate = service_rate_sum_21_days / float(NUM_21_DAYS) * 21.0
    avg_conception_rate = conception_rate_sum_21_days / float(NUM_21_DAYS)
    pregnancy_rate = avg_service_rate * avg_conception_rate

    return len(calves), \
           len(heiferIs), \
           len(heiferIIs), \
           len(heiferIIIs), \
           len(cows), \
           num_heiferII_preg, \
           num_cow_preg, \
           num_cow_milking, \
           parity_count_tuple, \
           num_cow_in_vwp, \
           avg_feed_cost, \
           avg_fixed_cost, \
           avg_repro_cost, \
           avg_milk_income, \
           total_replacement_bought, \
           total_replacement_cost, \
           total_heifer_sold, \
           total_heifer_value, \
           total_calf_sold, \
           total_calf_value, \
           total_slaughter_value, \
           avg_slaughter_value, \
           income_over_feed_cost, \
           net_return, \
           avg_service_rate * 100.0, \
           avg_conception_rate * 100.0, \
           pregnancy_rate * 100, \
           num_culled_range, \
           float(num_culled_range) / float(len(cows)) * 100, \
           cull_reason_stats_range

if __name__ == "__main__":
    calve_num_sum = 0 
    heiferI_num_sum = 0 
    heiferII_num_sum = 0 
    heiferIII_num_sum = 0 
    cow_num_sum = 0 
    num_heiferII_preg_sum = 0 
    num_cow_preg_sum = 0 
    num_cow_milking_sum = 0 
    parity_count_tuple_sum = {}
    num_cow_in_vwp_sum = 0 
    avg_feed_cost_sum = 0 
    avg_fixed_cost_sum = 0 
    avg_repro_cost_sum = 0 
    avg_milk_income_sum = 0 
    total_replacement_bought_sum = 0 
    total_replacement_cost_sum = 0 
    total_heifer_sold_sum = 0 
    total_heifer_value_sum = 0 
    total_calf_sold_sum = 0 
    total_calf_value_sum = 0 
    total_slaughter_value_sum = 0 
    avg_slaughter_value_sum = 0 
    income_over_feed_cost_sum = 0 
    net_return_sum = 0 
    avg_service_rate_sum = 0 
    avg_conception_rate_sum = 0 
    pregnancy_rate_sum = 0 
    num_culled_range_sum = 0 
    culling_rate_sum = 0 
    cull_reason_stats_range = {}

    for i in range(REPETITIONS):
        replacement_market = generate_replacement_herd(5000)
        calve_num, heiferI_num, heiferII_num, heiferIII_num, cow_num, num_heiferII_preg, num_cow_preg, num_cow_milking, parity_count_tuple, num_cow_in_vwp, avg_feed_cost, avg_fixed_cost, \
        avg_repro_cost, avg_milk_income, total_replacement_bought, total_replacement_cost, total_heifer_sold, total_heifer_value, total_calf_sold, total_calf_value, total_slaughter_value, \
        avg_slaughter_value, income_over_feed_cost, net_return, avg_service_rate, avg_conception_rate, pregnancy_rate, num_culled_range, culling_rate, cull_reason_stats_range = start_simulation(1000, 3000, replacement_market)

        calve_num_sum += calve_num 
        heiferI_num_sum += heiferI_num
        heiferII_num_sum += heiferII_num
        heiferIII_num_sum += heiferIII_num
        cow_num_sum += cow_num
        num_heiferII_preg_sum += num_heiferII_preg
        num_cow_preg_sum += num_cow_preg
        num_cow_milking_sum += num_cow_milking
        for parity, count in parity_count_tuple.items():
            if parity in parity_count_tuple_sum:
                parity_count_tuple_sum[parity] += count
            else:
                parity_count_tuple_sum[parity] = count
        num_cow_in_vwp_sum += num_cow_in_vwp 
        avg_feed_cost_sum += avg_feed_cost
        avg_fixed_cost_sum += avg_fixed_cost
        avg_repro_cost_sum += avg_repro_cost
        avg_milk_income_sum += avg_milk_income
        total_replacement_bought_sum += total_replacement_bought
        total_replacement_cost_sum += total_replacement_cost
        total_heifer_sold_sum += total_heifer_sold
        total_heifer_value_sum += total_heifer_value
        total_calf_sold_sum += total_calf_sold
        total_calf_value_sum += total_calf_value
        total_slaughter_value_sum += total_slaughter_value
        avg_slaughter_value_sum += avg_slaughter_value
        income_over_feed_cost_sum += income_over_feed_cost
        net_return_sum += net_return
        avg_service_rate_sum += avg_service_rate
        avg_conception_rate_sum += avg_conception_rate
        pregnancy_rate_sum += pregnancy_rate
        num_culled_range_sum += num_culled_range
        culling_rate_sum += culling_rate
        cull_reason_stats_range_sum = {}
        for cull_reason, count in cull_reason_stats_range.items():
            if cull_reason in cull_reason_stats_range_sum:
                cull_reason_stats_range_sum[cull_reason] += count
            else:
                cull_reason_stats_range_sum[cull_reason] = count

    print("\n=================== Herd structure at the end of the simulation ===================\n".format(config.econ_indicator_range))
    print("Total calves:\t\t\t{}".format(calve_num_sum / REPETITIONS))
    print("Total heiferI:\t\t\t{}".format(heiferI_num_sum / REPETITIONS))
    print("Total heiferII:\t\t\t{}".format(heiferII_num_sum / REPETITIONS))
    print("Total heiferIII:\t\t{}".format(heiferIII_num_sum / REPETITIONS))
    print("Total cows:\t\t\t{}".format(cow_num_sum / REPETITIONS))
    print("Total heiferII pregnant:\t{}".format(num_heiferII_preg_sum / REPETITIONS))
    print("Total cows pregnant:\t\t{}".format(num_cow_preg_sum / REPETITIONS))
    print("Total cows milking:\t\t{}".format(num_cow_milking_sum / REPETITIONS))
    for parity, count in parity_count_tuple_sum.items():
        print("Parity {}:\t\t\t {}".format(parity, count / REPETITIONS))
    print("Total cows in vwp:\t\t{}".format(num_cow_in_vwp_sum / REPETITIONS))

    print("\n=================== Last {} days economy stats ===================\n".format(config.econ_indicator_range))
    print("Feed cost:\t\t\t{0:.2f} $/cow/day".format(avg_feed_cost_sum / REPETITIONS))
    print("Fixed cost:\t\t\t{0:.2f} $/cow/day".format(avg_fixed_cost_sum / REPETITIONS))
    print("Repro cost:\t\t\t{0:.2f} $/cow/day".format(avg_repro_cost_sum / REPETITIONS))
    #print("Total breeding cost:\t\t{0:.2f} $".format(total_breeding_cost))
    #print("Total semen cost:\t\t{0:.2f} $".format(total_semen_cost))
    #print("Total ai cost:\t\t\t{0:.2f} $".format(total_ai_cost))
    #print("Total preg check cost:\t\t{0:.2f} $".format(total_preg_check_cost))
    print("Milk income:\t\t\t{0:.2f} $/cow/day".format(avg_milk_income_sum / REPETITIONS))
    print("Total replacement bought:\t{0:.2f}".format(total_replacement_bought_sum / REPETITIONS))
    print("Total replacement cost:\t\t{0:.2f} $".format(total_replacement_cost_sum / REPETITIONS))
    print("Total replacement sold:\t\t{0:.2f}".format(total_heifer_sold_sum / REPETITIONS))
    print("Total heifer sold income:\t{0:.2f} $".format(total_heifer_value_sum / REPETITIONS))
    print("Total calf sold:\t\t{0:.2f}".format(total_calf_sold_sum / REPETITIONS))
    print("Total calf sold income:\t\t{0:.2f} $".format(total_calf_value_sum / REPETITIONS))
    print("Total slaughter income:\t\t{0:.2f} $".format(total_slaughter_value_sum / REPETITIONS))
    print("Average slaughter income:\t{0:.2f} $".format(avg_slaughter_value_sum / REPETITIONS))
    print("IOFC: \t\t\t\t{0:.2f} $".format(income_over_feed_cost_sum / REPETITIONS))
    print("Net return: \t\t\t{0:.2f} $".format(net_return_sum / REPETITIONS))

    print("SR%: \t\t\t\t{0:.2f}%".format(avg_service_rate_sum / REPETITIONS))
    print("CR%: \t\t\t\t{0:.2f}%".format(avg_conception_rate_sum / REPETITIONS))
    print("PR%: \t\t\t\t{0:.2f}%".format(pregnancy_rate_sum / REPETITIONS))
    print("Total cows culled:\t\t{}".format(num_culled_range_sum / REPETITIONS))
    print("Culling rate: \t\t\t{0:.2f}%".format(culling_rate_sum / REPETITIONS))
    for cull_reason, count in cull_reason_stats_range_sum.items():
        print("{} => {}".format(cull_reason, count / REPETITIONS))
