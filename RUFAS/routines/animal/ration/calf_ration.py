from .hardcoded_ration import get_nutrient_rqmts, get_ration
import math


def optimize(feed, rqmts):
    return get_ration()


def calculate_rqmts():
    return get_nutrient_rqmts()

def calc_requirements(calf, temp, wean_day, wean_length, milk_type):
    '''
    Calculate dietary intake and nutrient requirements for the calf. 

    Args:
        calf: the calf to calculate the nutrient requirement for 
        temp: the average temperature of the simulation day
        wean_day: the wean day of the calf
        wean_length: the wean length of the calf
        milk_type: either "whole" or "replacer"
    '''
    # nutrient composition of feeds from the feed library
    whole_milk_dm = 12.5
    whole_milk_cp = 25.4
    whole_milk_me = 5.37

    milk_replacer_dm = 95
    milk_replacer_cp = 20
    milk_replacer_me = 4.75

    starter_dm = 90
    starter_cp = 18
    starter_me = 3.28
    
    if milk_type == "whole":
        milk_replacer_dm = 0
    else:
        whole_milk_dm = 0

    # milk-based feed intake
    whole_milk_intake = 0.1 * calf.birth_weight * whole_milk_dm * 0.01 
    milk_replacer_intake = 0.1 * calf.birth_weight * 0.15 * milk_replacer_dm * 0.01
    
    # starter intake
    if calf.body_weight <= 69.365:
        starter_intake = -0.24783 + 0.0049567 * calf.body_weight 
    else:
        starter_intake = -6.2263 + 0.091145 * calf.body_weight

    # reduction in intake during weaning
    wean_start = wean_day - wean_length - 1

    milk_reduct = round(0.5 * wean_length) 

    if whole_milk_intake != 0:
        milk_intake_wean = whole_milk_intake * (1 - milk_reduct / (wean_length + 1))
    else:
        milk_intake_wean = milk_replacer_intake * (1 - milk_reduct / (wean_length + 1))

    calf.dm_intake += whole_milk_intake + milk_replacer_intake + starter_intake
    calf.me_intake += whole_milk_me * whole_milk_intake + milk_replacer_me * milk_replacer_intake + starter_me * starter_intake
    calf.cp_intake += 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake + starter_cp * starter_intake)

    milk_me_proportion = (whole_milk_intake * whole_milk_me + milk_replacer_intake * milk_replacer_me) / calf.me_intake
    starter_me_proportion = starter_intake * starter_me / calf.me_intake

    calf.milk_starter_feed['milk'] += 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake)
    calf.milk_starter_feed['starter'] += 0.01 * starter_cp * starter_intake 
    
    adp_intake = (0.93 * calf.milk_starter_feed['milk'] / calf.cp_intake + 0.75 * calf.milk_starter_feed['starter'] / calf.cp_intake) * 1000

    milk_proportion = (whole_milk_intake + milk_replacer_intake) / calf.dm_intake
    starter_proportion = starter_intake / calf.dm_intake

    # maintainance requirements
    if calf.days_born <= 60:
        if temp < -30: 
            t_factor = 1.34
        elif temp < 15:
            t_factor = -0.0272 * temp + 0.4751 
        else:
            t_factor = 0     
    else:
        if temp < -30:
            t_factor = 1.07
        elif temp <= 5:
            t_factor = -0.0271 * temp + 0.2002
        else:
            t_factor = 0
    
    ne_maint = 0.086 * calf.body_weight ** 0.75 * (1 + t_factor) 
    me_maint = ne_maint / (0.86 * milk_proportion + 0.75 * starter_proportion)

    bio_val = 0.8 * calf.milk_starter_feed['milk'] / calf.cp_intake + 0.7 * calf.milk_starter_feed['starter'] / calf.cp_intake 

    endo_urine_N = 0.0002 * calf.body_weight ** 0.75 * 1000
    meta_fecal_N = (0.0019 * (whole_milk_intake + milk_replacer_intake) + 0.0033 * starter_intake) * 1000

    adp_maint = 6.25 * (1 / bio_val * (endo_urine_N + meta_fecal_N) - meta_fecal_N)

    # growth requirements
    me_gain = calf.me_intake - me_maint
    ne_gain = me_gain * (0.69 * milk_me_proportion + 0.57 * starter_me_proportion)

    if ne_gain >= 0:
        energy_allow_gain = math.exp(0.833 * math.log((1.19 * ne_gain)/(0.69 * calf.body_weight ** 0.355)))
    else:
        energy_allow_gain = 0
    
    adp_allow_gain = (adp_intake - adp_maint) * bio_val / 0.188 * 0.001
    live_weight_change = min(energy_allow_gain, adp_allow_gain)

    animal_intake = {
        'whole_milk_intake': whole_milk_intake,
        'milk_replacer_intake': milk_replacer_intake,
        'starter_intake': starter_intake,
        'wean_start': wean_start,
        'milk_reduction': milk_reduct,
        'milk_intake_wean': milk_intake_wean,
        'dm_intake': calf.dm_intake,
        'me_intake': calf.me_intake,
        'cp_intake': calf.cp_intake,
        'adp_intake': adp_intake,
        'milk_me_proportion': milk_me_proportion,
        'starter_me_proportion': starter_me_proportion,
        'milk_proportion': milk_proportion,
        'starter_proportion': starter_proportion        
    }

    nutrient_requirements = {
        'ne_maint': {'op': '=', 'val': ne_maint},
        'me_maint': {'op': '=', 'val': me_maint},
        'bio_val': {'op': '=', 'val': bio_val},
        'endo_urine_N': {'op': '=', 'val': endo_urine_N},
        'meta_fecal_N': {'op': '=', 'val': meta_fecal_N},
        'adp_maint': {'op': '=', 'val': adp_maint},
        'me_gain': {'op': '=', 'val': me_gain},
        'ne_gain': {'op': '=', 'val': ne_gain}, 
        'energy_allow_gain': {'op': '=', 'val': energy_allow_gain},
        'adp_allow_gain': {'op': '=', 'val': adp_allow_gain},
        'live_weight_change': {'op': '=', 'val': live_weight_change}
    }

    return animal_intake, nutrient_requirements

