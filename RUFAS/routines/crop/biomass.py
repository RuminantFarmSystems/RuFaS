'''
This module contains the necessary functions for calculating and updating the 
values in a CropType object. Currently the only function meant to be used 
outside of this file is the calculate_actual_Biomass() function. The other 
functions are meant to serve as helper functions within this file.

CropType values updated by calculate_actual_Biomass():
    dBiomass_max
    gamma_reg
    dBiomass_actual
    prev_biomass_actual
    biomass_actual
'''

from math import exp

def calculate_actual_Biomass(crop_type, time, weather):
    H_phosyn = calculate_intercepted_radiation(crop_type, time, weather)
    crop_type.dBiomass_max = crop_type.RUE * H_phosyn
    
    crop_type.gamma_reg = calculate_gamma_reg(crop_type, time, weather)
    crop_type.dBiomass_actual = crop_type.dBiomass_max * crop_type.gamma_reg
    crop_type.prev_biomass_actual = crop_type.biomass_actual
    crop_type.biomass_actual += crop_type.dBiomass_actual
    
def calculate_intercepted_radiation(crop_type, time, weather):
    H_day = weather.radiation[time.year][time.day]
    return 0.5 * H_day * (1 - exp(-1*crop_type.kl*crop_type.LAI_actual))

def calculate_gamma_reg(crop_type, time, weather):
    wstrs = calculate_wstrs(crop_type)
    tstrs = calculate_tstrs(crop_type, time, weather)
    nstrs = calculate_nstrs(crop_type)
    pstrs = calculate_pstrs(crop_type)
    
    crop_type.gamma_reg = 1- max(wstrs, tstrs, nstrs, pstrs)
    
    
'''
The following four functions comprise the "Growth Constraints".
This includes the water, temperature, nitrogen, and phosphorus stress
for a given day. These values are needed to calculate the gamma_reg value.
They do not modify the values of any State class.
'''

def calculate_wstrs(crop_type):
    return 1 - (crop_type.water_actual_up / crop_type.Et)
    
def calculate_tstrs(crop_type, time, weather):
    T_avg = weather.tAvg[time.year][time.day]
    T_opt = crop_type.T_opt
    T_base_min = crop_type.T_base_min
    
    if T_avg <= T_base_min:
        return 1
    
    elif T_base_min < T_avg  and T_avg <= T_opt:
        top_half_eq = -0.1054 * (T_opt - T_avg)**2
        bottom_half_eq = (T_avg - T_base_min)**2
        return 1 - exp(top_half_eq / bottom_half_eq)
    
    elif T_opt < T_avg and T_avg <= (2 * T_opt - T_base_min):
        top_half_eq = -0.1054 * (T_opt - T_avg)**2
        bottom_half_eq = (2*T_opt - T_avg - T_base_min)**2
        return 1 - exp(top_half_eq / bottom_half_eq)
    
    elif T_avg > (2*T_opt - T_base_min):
        return 1
    
def calculate_nstrs(crop_type):
    phi_n = 200 * ((crop_type.prev_bio_N/crop_type.prev_bio_N_opt) - 0.5)
    return 1 - phi_n / (phi_n + exp(3.535 - 0.02597*phi_n))   
    
def calculate_pstrs(crop_type):
    phi_p = 200 * ((crop_type.prev_bio_P/crop_type.prev_bio_P_opt) - 0.5)
    return 1 - phi_p / (phi_p + exp(3.535 - 0.02597 * phi_p))