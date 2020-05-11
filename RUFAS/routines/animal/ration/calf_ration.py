################################################################################
'''
RUFAS: Ruminant Farm Systems Model
File name: calf_ration.py
Description: Calculates the ration for calves.
Author(s): Militsa Sotirova, militsasotirova@gmail.com
'''
################################################################################
import math

def optimize(feed, rqmts):
    """
    TEMPORARY PLACEHOLDER
    Sets up the arguments for the linear programming optimization.

    Args:
        feed : instance of the Feed class
        rqmts : dict which represents the dietary requirements of the cows

    Returns:
    """
    return {'Corn_grain': 0.0, 'Cotton_seed': 6.0651063, 'Legume_hay': 13.669348, 'Roasted_soybean': 2.4089406, 'Rye_hay': 0.0, 'status': 'Optimal', 'objective': 4.536948317}

def calculate_rqmts():
    """
    TEMPORARY PLACEHOLDER
    Calculate the dietary requirements of the animals. These values are used
    on the RHS of the linear program. Each calculation has a reference to the
    respective calculation in the pseudocode.

    Args:

    Returns:
        dict : a dictionary that represents the dietary requirements of the cows,
            where the left hand side is nutrients_list and the right hand side is
            calculated in this method
        DMIest: dry matter intake estimation, kg
        DBW: Body weight change (delta body weight = DBW), kg
    """
    nutrient_rqmts = {'FU': {'op': '<=', 'val': 7.566673489860807}, 'RU': {'op': '>=', 'val': 0}, 'ME_DM': {'op': '>=', 'val': 57.238188330372566}, 'RDP_DM': {'op': '>=', 'val': 2.0347001114951313}, 'RUP_DM': {'op': '>=', 'val': 1.2716733909335047}}
    DMIest = 27.620363504458798 
    DBW = -0.4125
    return nutrient_rqmts, DMIest, DBW



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

# total intake
dm_intake = 0
me_intake = 0
cp_intake = 0
milk_starter_feed = {}

'''
    Calculate dietary intake and nutrient requirements for the calf. 
'''
def calc_requirements(temp, wean_day, wean_length, milk_type, birth_weight, body_weight, days_born):
    if milk_type == "whole":
        milk_replacer_dm = 0
    else:
        whole_milk_dm = 0

    # milk-based feed intake
    whole_milk_intake = 0.1 * birth_weight * whole_milk_dm * 0.01 
    milk_replacer_intake = 0.1 * birth_weight * 0.15 * milk_replacer_dm * 0.01
    
    # starter intake
    if body_weight <= 69.365:
        starter_intake = -0.24783 + 0.0049567 * body_weight 
    else:
        starter_intake = -6.2263 + 0.091145 * body_weight

    # reduction in intake during weaning
    wean_start = wean_day - wean_length - 1

    milk_reduct = round(0.5 * wean_length) 

    if whole_milk_intake != 0:
        milk_intake_wean = whole_milk_intake * (1 - milk_reduct / (wean_length + 1))
    else:
        milk_intake_wean = milk_replacer_intake * (1 - milk_reduct / (wean_length + 1))
    
    # total intake
    global dm_intake
    global me_intake
    global cp_intake
    global milk_starter_feed

    dm_intake += whole_milk_intake + milk_replacer_intake + starter_intake
    me_intake += whole_milk_me * whole_milk_intake + milk_replacer_me * milk_replacer_intake + starter_me * starter_intake
    cp_intake += 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake + starter_cp * starter_intake)

    milk_me_proportion = (whole_milk_intake * whole_milk_me + milk_replacer_intake * milk_replacer_me) / me_intake
    starter_me_proportion = starter_intake * starter_me / me_intake

    milk_starter_feed['milk'] += 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake)
    milk_starter_feed['starter'] += 0.01 * starter_cp * starter_intake 
    
    adp_intake = (0.93 * milk_starter_feed['milk'] / cp_intake + 0.75 * milk_starter_feed['starter'] / cp_intake) * 1000

    milk_proportion = (whole_milk_intake + milk_replacer_intake) / dm_intake
    starter_proportion = starter_intake / dm_intake

    # maintainance requirements
    if days_born <= 60:
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
    
    ne_maint = 0.086 * body_weight ** 0.75 * (1 + t_factor) 
    me_maint = ne_maint / (0.86 * milk_proportion + 0.75 * starter_proportion)

    bio_val = 0.8 * milk_starter_feed['milk'] / cp_intake + 0.7 * milk_starter_feed['starter'] / cp_intake 

    endo_urine_N = 0.0002 * body_weight ** 0.75 * 1000
    meta_fecal_N = (0.0019 * (whole_milk_intake + milk_replacer_intake) + 0.0033 * starter_intake) * 1000

    adp_maint = 6.25 * (1 / bio_val * (endo_urine_N + meta_fecal_N) - meta_fecal_N)

    # growth requirements
    me_gain = me_intake - me_maint
    ne_gain = me_gain * (0.69 * milk_me_proportion + 0.57 * starter_me_proportion)

    energy_allow_gain = math.exp(0.833 * math.log((1.19 * ne_gain)/(0.69 * body_weight ** 0.355)))
    adp_allow_gain = (adp_intake - adp_maint) * bio_val / 0.188 * 0.001
    live_weight_change = min(energy_allow_gain, adp_allow_gain)

    animal_intake = {
        'whole_milk_intake': whole_milk_intake,
        'milk_replacer_intake': milk_replacer_intake,
        'starter_intake': starter_intake,
        'wean_start': wean_start,
        'milk_reduction': milk_reduct,
        'milk_intake_wean': milk_intake_wean,
        'dm_intake': dm_intake,
        'me_intake': me_intake,
        'cp_intake': cp_intake,
        'adp_intake': adp_intake,
        'milk_me_proportion': milk_me_proportion,
        'starter_me_proportion': starter_me_proportion,
        'milk_proportion': milk_proportion,
        'starter_proportion': starter_proportion        
    }

    nutrient_requirements = {
        'ne_maint': ne_maint,
        'me_maint': me_maint,
        'bio_val': bio_val,
        'endo_urine_N': endo_urine_N,
        'meta_fecal_N': meta_fecal_N,
        'adp_maint': adp_maint,
        'me_gain': me_gain,
        'ne_gain': ne_gain, 
        'energy_allow_gain': energy_allow_gain,
        'adp_allow_gain': adp_allow_gain,
        'live_weight_change': live_weight_change
    }

    return animal_intake, nutrient_requirements
