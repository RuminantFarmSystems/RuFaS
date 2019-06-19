#! ./env/bin/python3
'''
RUFAS: Ruminant Farm Systems Model
File name: herd_simulation.py
Author(s): Manfei Li, mli497@wisc.edu
Description: This file simulates the whole herd with herd size and simulation length

'''
import matplotlib as mpl
mpl.use('TkAgg')
import matplotlib.pyplot as plt
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

'''
		Description:
			generate a replacement herd to simulate the market, for the herd to get replacements
		Input:
			max_num: the max number of this replacement herd
            sim_days: simulation length of this herd, to make sure they reach to the heiferIII stage
		Output:
			cows: ready to enter the herd
	'''
def initialize_herd(calf_num, heiferI_num, heiferII_num, heiferIII_num, cow_num, replace_num, sim_days=1500):
    calves = []
    heiferIs = []
    heiferIIs = []
    heiferIIIs = []
    cows = []

    res_calves = []
    res_heiferIs = []
    res_heiferIIs = []
    res_heiferIIIs = []
    res_cows = []

    for _ in range(calf_num + heiferI_num + heiferII_num + heiferIII_num + cow_num + replace_num):
        args = {
            'breed': 'HO',
            'date': 0,
            'days_born': 0
        }
        new_calf = Calf(args)
        if not (new_calf._culled or new_calf._sold):
            calves.append(new_calf)

    while len(res_calves) < calf_num:
        calf = calves.pop()
        calf._events.add_event(calf._days_born, 'Entered Herd')
        res_calves.append(calf)

    for date in range(sim_days):
        for calf in calves:
            wean_day = calf.update()
            if wean_day:
                new_heiferI = HeiferI(calf)
                if len(res_heiferIs) < heiferI_num:
                    res_heiferIs.append(new_heiferI)
                    new_heiferI._events.add_event(new_heiferI._days_born, 'Entered Herd')
                else:
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
                if len(res_heiferIIs) < heiferII_num:
                    res_heiferIIs.append(new_heiferII)
                    new_heiferII._events.add_event(new_heiferII._days_born, 'Entered Herd')
                else:
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
                if len(res_heiferIIIs) < heiferIII_num:
                    res_heiferIIIs.append(new_heiferIII)
                    new_heiferIII._events.add_event(new_heiferIII._days_born, 'Entered Herd')
                else:
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
                if len(res_cows) < cow_num:
                    res_cows.append(new_cow)
                    new_cow._events.add_event(new_cow._days_born, 'Entered Herd')
                else:
                    cows.append(new_cow)
                heiferIIIs.remove(heiferIII)

    return res_calves, res_heiferIs, res_heiferIIs, res_heiferIIIs, res_cows, cows

'''
		Description:
			the simulation updates
		Input:
			herd_num: the lactating and dry herd number
            sim_length: the length of the main simulation
            replace_market: call the replacement_market to have the extra heiferIIIs
		Output:
	'''
def start_simulation(herd_num, sim_length, calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement_market):
    start_date = 0

    # print(len(calves))
    # stats init
    sold_calves = []
    sold_heifers = []
    culled_heifers = []
    culled_cows = []
    total_culled = 0
    total_new_born = 0
    sold_to_market = 0
    bought_from_market = 0

    #figures
    daily_calf_num = []
    daily_heiferI_num = []
    daily_heiferII_num = []
    daily_heiferIII_num = []
    daily_cow_num = []
    culled_cows_lst = []
    heifer_sold_lst = []
    replacement_bought_lst = []
    milking_cows_lst = []

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

    count_21_days = 0
    num_ai_21_days = 0
    num_cow_btw_vwp_preg_21_days = 0
    service_rate_sum_21_days = 0
    num_preg_21_days = 0
    num_ai_21_days = 0
    conception_rate_sum_21_days = 0


# record the last days stats
    for date in range(sim_length):
        daily_cow_cull_num = 0
        daily_heifer_sold = 0
        daily_bought_from_market = 0
        daily_cow_milking = 0
        daily_calf_num.append(len(calves))
        daily_heiferI_num.append(len(heiferIs))
        daily_heiferII_num.append(len(heiferIIs))
        daily_heiferIII_num.append(len(heiferIIIs))
        daily_cow_num.append(len(cows))

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
            # if date == 50:
            #     print(len(calves))
            #     print(calves[0])
            #     return

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
        while len(heiferIIIs) + len(cows) > herd_num * 1.03:
            heiferIIIs.pop()
            sold_to_market += 1
            daily_heifer_sold += 1
            if record_econ_stats:
                total_heifer_sold += 1
                total_heifer_value += config.heifer_sell_price

# if the number of heifers is less than needed for the herd, buy replacement from the market
        while len(cows) + len(heiferIIIs) < herd_num * 1.01 and date > 1:
            replacement_market[0]._events.add_event(replacement_market[0]._days_born, 'Entered Herd')
            cows.append(replacement_market[0])
            bought_from_market += 1
            daily_bought_from_market += 1
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

                if cow._cull_reason in cull_reason_stats:
                    cull_reason_stats[cow._cull_reason] += 1
                else:
                    cull_reason_stats[cow._cull_reason] = 1
                total_culled += 1
                daily_cow_cull_num += 1

                
                culled_cows.append(cow)
                #print(len(culled_cows))
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
                    new_calf._events.add_event(new_calf._days_born, 'Entered Herd')
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
            
            if cow._milking:
                daily_cow_milking += 1

        #caculate service rate and conception rate
        if date >= sim_length - 21 * NUM_21_DAYS:
            count_21_days += 1
            if count_21_days % 21 == 0:
                service_rate_sum_21_days += float(num_ai_21_days) / float(num_cow_btw_vwp_preg_21_days)
                conception_rate_sum_21_days += float(num_preg_21_days) / float(num_ai_21_days)
                num_ai_21_days = 0
                num_cow_btw_vwp_preg_21_days = 0
                num_preg_21_days = 0

        # for figures
        culled_cows_lst.append(daily_cow_cull_num)
        heifer_sold_lst.append(daily_heifer_sold)
        replacement_bought_lst.append(daily_bought_from_market)
        milking_cows_lst.append(daily_cow_milking)

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
        avg_feed_cost = total_feed_cost/365/daily_cow_milking
        total_fixed_cost += fixed_cost
        avg_fixed_cost = total_fixed_cost/365/1000
        total_milk_income += milk_income
        avg_milk_income = total_milk_income/365/daily_cow_milking
        income_over_feed_cost = total_milk_income + total_slaughter_value + total_heifer_value + total_calf_value - total_feed_cost
        net_return = income_over_feed_cost - total_replacement_cost - total_fixed_cost

    
        


    parity_lst = [cow._calves if cow._calves <= 2 else '3+' for cow in cows ]
    parity_count_tuple = Counter(parity_lst)
    avg_service_rate = service_rate_sum_21_days / float(NUM_21_DAYS) * 21.0
    avg_conception_rate = conception_rate_sum_21_days / float(NUM_21_DAYS)
    pregnancy_rate = avg_service_rate * avg_conception_rate

    print("\n=================== Herd structure at the end of the simulation ===================\n".format(config.econ_indicator_range))
    print("Total calves:\t\t\t{}".format(len(calves)))
    print("Total heiferI:\t\t\t{}".format(len(heiferIs)))
    print("Total heiferII:\t\t\t{}".format(len(heiferIIs)))
    print("Total heiferIII:\t\t{}".format(len(heiferIIIs)))
    print("Total cows:\t\t\t{}".format(len(cows)))
    print("Total heiferII pregnant:\t{}".format(num_heiferII_preg))
    print("Total cows pregnant:\t\t{}".format(num_cow_preg))
    print("Total cows milking:\t\t{}".format(num_cow_milking))
    for parity, count in parity_count_tuple.items():
        print("Parity {}:\t\t\t {}".format(parity, count))
    print("Total cows in vwp:\t\t{}".format(num_cow_in_vwp))

    print("\n=================== Last {} days economy stats ===================\n".format(config.econ_indicator_range))
    print("Feed cost:\t\t\t{0:.2f} $/cow/day".format(avg_feed_cost))
    print("Fixed cost:\t\t\t{0:.2f} $/cow/day".format(avg_fixed_cost))
    print("Repro cost:\t\t\t{0:.2f} $/cow/day".format(avg_repro_cost))
    #print("Total breeding cost:\t\t{0:.2f} $".format(total_breeding_cost))
    #print("Total semen cost:\t\t{0:.2f} $".format(total_semen_cost))
    #print("Total ai cost:\t\t\t{0:.2f} $".format(total_ai_cost))
    #print("Total preg check cost:\t\t{0:.2f} $".format(total_preg_check_cost))
    print("Milk income:\t\t\t{0:.2f} $/cow/day".format(avg_milk_income))
    print("Total replacement bought:\t{0:.2f}".format(total_replacement_bought))
    print("Total replacement cost:\t\t{0:.2f} $".format(total_replacement_cost))
    print("Total replacement sold:\t\t{0:.2f}".format(total_heifer_sold))
    print("Total heifer sold income:\t{0:.2f} $".format(total_heifer_value))
    print("Total calf sold:\t\t{0:.2f}".format(total_calf_sold))
    print("Total calf sold income:\t\t{0:.2f} $".format(total_calf_value))
    print("Total slaughter income:\t\t{0:.2f} $".format(total_slaughter_value))
    print("Average slaughter income:\t{0:.2f} $".format(avg_slaughter_value))
    print("IOFC: \t\t\t\t{0:.2f} $".format(income_over_feed_cost))
    print("Net return: \t\t\t{0:.2f} $".format(net_return))

    print("SR%: \t\t\t\t{0:.2f}%".format(avg_service_rate * 100.0))
    print("CR%: \t\t\t\t{0:.2f}%".format(avg_conception_rate * 100.0))
    print("PR%: \t\t\t\t{0:.2f}%".format(pregnancy_rate * 100.0))
    print("Total cows culled:\t\t{}".format(num_culled_range))
    print("Culling rate: \t\t\t{0:.2f}%".format(float(num_culled_range) / float(len(cows)) * 100))
    for cull_reason, count in cull_reason_stats_range.items():
        print("{} => {}".format(cull_reason, count))
    # for parity, count in parity_culling_stats_range.items():
    #     print("Parity {} total culls: {}".format(parity, count))


    #@staticmethod
    draw_stat(daily_calf_num, daily_heiferI_num, daily_heiferII_num, daily_heiferIII_num, daily_cow_num, culled_cows_lst, heifer_sold_lst, replacement_bought_lst, milking_cows_lst, sim_length) 
    # draw curves for a cow
    print(cows[0])
    cows[0].draw_curves()

    print(cows[20])
    cows[20].draw_curves()

    print(cows[150])
    cows[150].draw_curves()

def draw_stat(daily_calf_num, daily_heiferI_num, daily_heiferII_num, daily_heiferIII_num, daily_cow_num, culled_cows_lst, heifer_sold_lst, replacement_bought_lst, milking_cows_lst, sim_length):    
    fig = plt.figure()
    x = [date for date in range(sim_length)]

    ax1 = fig.add_subplot(521)
    ax1.scatter(x, daily_calf_num, s=1)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.set_title("Number of calves each day")
        
    ax2 = fig.add_subplot(522)
    ax2.scatter(x, daily_heiferI_num, s=1)
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax2.set_title("Number of heiferIs each day")
        
    ax3 = fig.add_subplot(523)
    ax3.scatter(x, daily_heiferII_num, s=1)
    ax3.spines['right'].set_visible(False)
    ax3.spines['top'].set_visible(False)
    ax3.set_title("Number of heiferIIs each day")
        
    ax4 = fig.add_subplot(524)
    ax4.scatter(x, daily_heiferIII_num, s=1)
    ax4.spines['right'].set_visible(False)
    ax4.spines['top'].set_visible(False)
    ax4.set_title("Number of heiferIIIs each day")
    
    ax5 = fig.add_subplot(525)
    ax5.scatter(x, daily_cow_num, s=1)
    ax5.spines['right'].set_visible(False)
    ax5.spines['top'].set_visible(False)
    ax5.set_title("Number of cows each day")
        
    ax6 = fig.add_subplot(526)
    ax6.scatter(x, culled_cows_lst, s=1)
    ax6.spines['right'].set_visible(False)
    ax6.spines['top'].set_visible(False)
    ax6.set_title("Number of culled cows each day")
        
    ax7 = fig.add_subplot(527)
    ax7.scatter(x, heifer_sold_lst, s=1)
    ax7.spines['right'].set_visible(False)
    ax7.spines['top'].set_visible(False)
    ax7.set_title("Number of sold heifers each day")
        
    ax8 = fig.add_subplot(528)
    ax8.scatter(x, replacement_bought_lst, s=1)
    ax8.spines['right'].set_visible(False)
    ax8.spines['top'].set_visible(False)
    ax8.set_title("Number of bought heifers each day")
    
    # ax9 = fig.add_subplot(529)
    # ax9.scatter(x, milking_cows_lst, s=1)
    # ax9.spines['right'].set_visible(False)
    # ax9.spines['top'].set_visible(False)
    # ax9.set_title("Number of milking cows each day")
    
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.4)
    plt.show()  


if __name__ == "__main__":
    calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement_market = initialize_herd(160, 800, 820, 50, 1000, 5000)
    start_simulation(1000, 3000, calves, heiferIs, heiferIIs, heiferIIIs, cows, replacement_market)


