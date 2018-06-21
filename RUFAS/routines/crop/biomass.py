'''
RUFAS: Ruminant Farm Systems Model

File name: biomass.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the biomass values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

Variable definitions:

    H_day = incident total solar (MJ m^-2)

    kl = light extinction coefficient

    LAI = Leaf Area Index

    H_phosyn = Amount of intercepted photosynthetically active radiation on a
               given day. (MJ m^-2)

    RUE = Crop-specific radiation use efficiency (10^-1 g/MJ)

    dBiomass_max = Maximum potential biomass increase on current day

    dBiomass_actual = Actual increase in total plant biomass on a given day (kg ha^-1)

    biomass_actual = Total plant biomass on a given day

    bio_N = Actual mass of nitrogen stored in plant material (kg N ha^-1)

    bio_N_opt = Optimal mass of nitrogen stored in plant material for current
                growth stage (kg N ha^-1)

    phi_N = Scaling factor for nitrogen stress

    bio_P = Actual mass of phosphorus stored in plant material (kg P ha^-1)

    bio_P_opt = Optimal mass of phosphorus stored in plant material for current
                growth stage (kg P ha^-1)

    phi_P = scaling factor for phosphorus stress

    wstrs = Water stress for a given day

    tstrs = Temperature stress for a given day

    nstrs = Nitrogen strss for a given day

    pstrs = Phosphorus stress for a given day

    gamma_reg = Plant growth factor


CropType values updated by update_all():
    dBiomass_max
    gamma_reg
    dBiomass_actual
    prev_biomass_actual
    biomass_actual
'''
###############################################################################

from math import exp

#
# This function updates all biomass information
#
def update_all(crop_type, time, weather):
    # update gamma_reg value and record growth constraints in results
    results = calc_gamma_reg(crop_type, time, weather)
    record_gammareg_results(crop_type, time, results)

    # update biomass values
    calc_actual_Biomass(crop_type, time, weather)
    record_biomass_results(crop_type, time, weather)


#
# Calculate current actual biomass.
#
def calc_actual_Biomass(crop_type, time, weather):
    H_phosyn = calc_intercepted_radiation(crop_type, time, weather)

    # "Pseudo code_SC_maxdeltabio_1.0.docx" section 1.E.2
    crop_type.dBiomass_max = crop_type.RUE * H_phosyn

    # "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.A.2
    crop_type.dBiomass_actual = crop_type.dBiomass_max * crop_type.gamma_reg

    # Save value as previous day's value
    crop_type.prev_biomass_actual = crop_type.biomass_actual

    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date
    # Update current actual biomass
    if inGrowingPeriod:
        crop_type.biomass_actual += crop_type.dBiomass_actual
    else:
        crop_type.biomass_actual = 0


#
# Calculates amount of intercepted photosynthetically active radiation
# on a given day (MJ m^-2).
# "Pseudo code_SC_maxdeltabio_1.0.docx" section 1.E.1
#
def calc_intercepted_radiation(crop_type, time, weather):
    H_day = weather.radiation[time.year-1][time.day-1]
    return 0.5 * H_day * (1 - exp(-1*crop_type.kl*crop_type.LAI_actual))


#
# Calculates plant growth factor (AKA gamma_reg).
# "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.A.1
#
def calc_gamma_reg(crop_type, time, weather):
    wstrs = calc_wstrs(crop_type)
    tstrs = calc_tstrs(crop_type, time, weather)
    nstrs = calc_nstrs(crop_type)
    pstrs = calc_pstrs(crop_type)
    
    crop_type.gamma_reg = 1- max(wstrs, tstrs, nstrs, pstrs)

    return (wstrs, tstrs, nstrs, pstrs)


'''
The following four functions comprise the "Growth Constraints".
This includes the water, temperature, nitrogen, and phosphorus stress
for a given day. These values are needed to calculate the gamma_reg value.
They do not modify the values of any State class.
'''

#
# Calculates water stress for a given day
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.1
#
def calc_wstrs(crop_type):
    if crop_type.Et == 0:
        return 0
    result = 1.0 - (crop_type.water_actual_up / crop_type.Et)
    if result < 0:
        return 0
    else:
        return min(0.99, result)


#
# Calculates temperature stress for a given day.
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.2
#
def calc_tstrs(crop_type, time, weather):
    T_avg = weather.T_avg[time.year-1][time.day-1]
    T_opt = crop_type.T_opt
    T_base_min = crop_type.T_base_min
    MAX = 0.99
    result = 0
    if T_avg <= T_base_min:
        result = MAX
    
    elif T_base_min < T_avg  and T_avg <= T_opt:
        top_half_eq = -0.1054 * (T_opt - T_avg)**2
        bottom_half_eq = (T_avg - T_base_min)**2
        result = 1 - exp(top_half_eq / bottom_half_eq)
    
    elif T_opt < T_avg and T_avg <= (2 * T_opt - T_base_min):
        top_half_eq = -0.1054 * (T_opt - T_avg)**2
        bottom_half_eq = (2*T_opt - T_avg - T_base_min)**2
        result = 1 - exp(top_half_eq / bottom_half_eq)
    
    else: # T_avg > (2*T_opt - T_base_min):
        result = MAX

    return min(result, MAX)


#
# Calculates nitrogen stress for a given day.
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.3.2
#
def calc_nstrs(crop_type):
    if crop_type.bio_N_opt == 0:
        return 0
    phi_n = calc_phi_N(crop_type)
    result = 1 - phi_n / (phi_n + exp(3.535 - 0.02597*phi_n))
    return min(0.99, result)


#
# Calculates nitrogen stress scaling factor.
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.3.1
#
def calc_phi_N(crop_type):
    if crop_type.bio_N_opt == 0:
        return 300
    else:
        result = 200 * ((crop_type.bio_N/crop_type.bio_N_opt) - 0.5)
        return max(0, result)


#
# Calculates phosphorus stress scaling factor.
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.4.2
#
def calc_pstrs(crop_type):
    if crop_type.bio_P_opt == 0:
        return 0
    phi_p = calc_phi_P(crop_type)
    result = 1 - phi_p / (phi_p + exp(3.535 - 0.02597 * phi_p))
    return min(0.99, result)


#
# Calculates phosphorus stress scaling factor.
# "Pseudo code_SC_growth constraints_1.0.docx" section 6.4.1
#
def calc_phi_P(crop_type):
    if crop_type.bio_P_opt == 0:
        return 300
    else:
        return 200 * ((crop_type.bio_P/crop_type.bio_P_opt) - 0.5)


#==============================================================================

''' The following can be used for testing purposes '''


# The file that will record results of the biomass calculations.
biomass_test_file = "tests/crop_test_files/biomass_results.csv"

#
# The following will record the biomass calculations into the test file.
#
def record_biomass_results(crop_type, time, weather):
    if time.day == 1 and time.year == 1:
        reset_file(biomass_test_file)
    H_phosyn = calc_intercepted_radiation(crop_type, time, weather)
    with open(biomass_test_file, "a") as testResults:
        results = "%i,%f,%f,%f,%f,%f,%f\n" % (
            time.day,
            weather.radiation[time.year - 1][time.day - 1],
            H_phosyn,
            crop_type.dBiomass_max,
            crop_type.gamma_reg,
            crop_type.dBiomass_actual,
            crop_type.biomass_actual
        )

        if time.day == 1 and time.year == 1:
            testResults.write("Day,H_day,Hphosyn,dbiomax,gamma reg, dbioactual,bioactual\n")

        testResults.write(results)



# The file that will record results of the gamma reg calculations.
gammareg_test_file = "tests/crop_test_files/gammareg_results.csv"

#
# The following will record the gammareg calculations into the test file.
#
def record_gammareg_results(crop_type, time, results):
    wstrs, tstrs, nstrs, pstrs = results

    if time.day == 1 and time.year == 1:
        reset_file(gammareg_test_file)

    with open(gammareg_test_file, "a") as testResults:
        info = "%i,%f,%f,%f,%f,%f\n" % \
               (time.day, wstrs, tstrs, nstrs, pstrs, crop_type.gamma_reg)

        if time.day == 1 and time.year == 1:
            testResults.write("day,wstrs,tstrs,nstrs,pstrs,gamma_reg\n")

        testResults.write(info)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass