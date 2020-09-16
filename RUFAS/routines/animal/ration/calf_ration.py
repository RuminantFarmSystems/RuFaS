from .hardcoded_ration import get_nutrient_rqmts, get_ration
import math
import sqlite3


def optimize(feed, rqmts):
    return get_ration()

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
    whole_milk_id = 155
    milk_replacer_id = 156
    starter_id = 157

    conn = sqlite3.connect('input/databases/feeds.sqlite')
    cur = conn.cursor()
    cur.execute('SELECT * FROM nutrients WHERE feed_id = ?', (whole_milk_id,))
    whole_milk = cur.fetchone()
    whole_milk_dm = whole_milk[2]
    whole_milk_cp = whole_milk[3]
    whole_milk_de = whole_milk[26]
    # [A.1B.C.1]
    whole_milk_me = 0.96 * whole_milk_de

    cur.execute('SELECT * FROM nutrients WHERE feed_id = ?', (milk_replacer_id,))
    milk_replacer = cur.fetchone()
    milk_replacer_dm = milk_replacer[2]
    milk_replacer_cp = milk_replacer[3]
    milk_replacer_de = milk_replacer[26]
    # [A.1B.C.1]
    milk_replacer_me = 0.96 * milk_replacer_de

    cur.execute('SELECT * FROM nutrients WHERE feed_id = ?', (starter_id,))
    starter = cur.fetchone()
    starter_cp = starter[3]
    starter_de = starter[26]
    starter_ee = starter[6]
    # [A.1B.C.2]
    starter_me = (1.01 * starter_de - 0.45) + 0.0046 * (starter_ee - 3)
    conn.close()
    
    if milk_type == "whole":
        milk_replacer_dm = 0
    else:
        whole_milk_dm = 0

    # milk-based feed intake
    # [A.1B.A.1]
    whole_milk_intake = 0.1 * calf.birth_weight * whole_milk_dm * 0.01 
    # [A.1B.A.2]
    milk_replacer_intake = 0.1 * calf.birth_weight * 0.15 * milk_replacer_dm * 0.01
    
    # starter intake
    # [A.1B.A.3]
    if calf.body_weight <= 69.365:
        starter_intake = -0.24783 + 0.0049567 * calf.body_weight 
    else:
        starter_intake = -6.2263 + 0.091145 * calf.body_weight

    # reduction in intake during weaning
    # [A.1B.B.1]
    wean_start = wean_day - wean_length - 1
    # [A.1B.B.2]
    milk_reduct = round(0.5 * wean_length) 

    # [A.1B.B.3]
    if whole_milk_intake != 0:
        milk_intake_wean = whole_milk_intake * (1 - milk_reduct / (wean_length + 1))
    else:
        milk_intake_wean = milk_replacer_intake * (1 - milk_reduct / (wean_length + 1))

    # [A.1B.D.1]
    dm_intake = whole_milk_intake + milk_replacer_intake + starter_intake
    # [A.1B.C.4]
    me_intake = whole_milk_me * whole_milk_intake + milk_replacer_me * milk_replacer_intake + starter_me * starter_intake
    # [A.1B.E.1]
    cp_intake = 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake + starter_cp * starter_intake)

    # [A.1B.C.5]
    milk_me_proportion = (whole_milk_intake * whole_milk_me + milk_replacer_intake * milk_replacer_me) / me_intake
    # [A.1B.C.6]
    starter_me_proportion = starter_intake * starter_me / me_intake

    # [A.1B.E.2]
    milk_cp_intake = 0.01 * (whole_milk_cp * whole_milk_intake + milk_replacer_cp * milk_replacer_intake)
    starter_cp_intake = 0.01 * starter_cp * starter_intake 
    adp_intake = (0.93 * milk_cp_intake / cp_intake + 0.75 * starter_cp_intake / cp_intake) * 1000

    # [A.1B.D.2]
    milk_proportion = (whole_milk_intake + milk_replacer_intake) / dm_intake
    # [A.1B.D.3]
    starter_proportion = starter_intake / dm_intake

    # maintainance requirements
    # [A.1B.F.1]
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
    
    # [A.1B.F.2]
    ne_maint = 0.086 * calf.body_weight ** 0.75 * (1 + t_factor) 
    # [A.1B.F.3]
    me_maint = ne_maint / (0.86 * milk_proportion + 0.75 * starter_proportion)

    # [A.1B.G.1]
    bio_val = 0.8 * milk_cp_intake / cp_intake + 0.7 * starter_cp_intake / cp_intake 

    # [A.1B.G.2]
    endo_urine_N = 0.0002 * calf.body_weight ** 0.75 * 1000
    # [A.1B.G.3]
    meta_fecal_N = (0.0019 * (whole_milk_intake + milk_replacer_intake) + 0.0033 * starter_intake) * 1000

    # [A.1B.G.4]
    adp_maint = 6.25 * (1 / bio_val * (endo_urine_N + meta_fecal_N) - meta_fecal_N)

    # growth requirements
    # [A.1B.H.1]
    me_gain = me_intake - me_maint
    # [A.1B.H.2]
    ne_gain = me_gain * (0.69 * milk_me_proportion + 0.57 * starter_me_proportion)

    # [A.1B.H.3]
    if ne_gain >= 0:
        energy_allow_gain = math.exp(0.833 * math.log((1.19 * ne_gain)/(0.69 * calf.body_weight ** 0.355)))
    else:
        energy_allow_gain = 0
    
    # [A.1B.H.4]
    adp_allow_gain = (adp_intake - adp_maint) * bio_val / 0.188 * 0.001
    # [A.1B.H.5]
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

