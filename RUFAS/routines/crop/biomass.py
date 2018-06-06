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
    results = calculate_gamma_reg(crop_type, time, weather)
    record_gammareg_results(crop_type, time, results)

    # update biomass values
    calculate_actual_Biomass(crop_type, time, weather)
    H_phosyn_result = calculate_intercepted_radiation(crop_type, time, weather)
    record_biomass_results(crop_type, time, weather, H_phosyn_result)


#
#
#
def calculate_actual_Biomass(crop_type, time, weather):
    H_phosyn = calculate_intercepted_radiation(crop_type, time, weather)
    crop_type.dBiomass_max = crop_type.RUE * H_phosyn

    crop_type.dBiomass_actual = crop_type.dBiomass_max * crop_type.gamma_reg
    crop_type.prev_biomass_actual = crop_type.biomass_actual

    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date

    if inGrowingPeriod:
        crop_type.biomass_actual += crop_type.dBiomass_actual
    else:
        crop_type.biomass_actual = 0


#
#
#
def calculate_intercepted_radiation(crop_type, time, weather):
    H_day = weather.radiation[time.year-1][time.day-1]
    return 0.5 * H_day * (1 - exp(-1*crop_type.kl*crop_type.LAI_actual))


#
# gamma_reg represents "plant growth factor"
#
def calculate_gamma_reg(crop_type, time, weather):
    wstrs = calculate_wstrs(crop_type)
    tstrs = calculate_tstrs(crop_type, time, weather)
    nstrs = calculate_nstrs(crop_type)
    pstrs = calculate_pstrs(crop_type)
    
    crop_type.gamma_reg = 1- max(wstrs, tstrs, nstrs, pstrs)

    return (wstrs, tstrs, nstrs, pstrs)


'''
The following four functions comprise the "Growth Constraints".
This includes the water, temperature, nitrogen, and phosphorus stress
for a given day. These values are needed to calculate the gamma_reg value.
They do not modify the values of any State class.
'''

def calculate_wstrs(crop_type):
    if crop_type.Et == 0:
        return 0
    result = 1.0 - (crop_type.water_actual_up / crop_type.Et)
    if result < 0:
        return 0
    else:
        return min(0.99, result)


def calculate_tstrs(crop_type, time, weather):
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
    
    elif T_avg > (2*T_opt - T_base_min):
        result = MAX

    else:
        ''' 
        Should have hit one of the preceding cases. Not sure if they cover
        all possible cases though.
        '''

        print("Error: Did not hit one of the cases for calculate_tstrs.")
        print("Check if T_opt and T_base_min input values are correct")
        print("Exiting program")
        exit()

    return min(result, MAX)


def calculate_nstrs(crop_type):
    if crop_type.bio_N_opt == 0:
        return 0
    phi_n = calc_phi_N(crop_type)
    result = 1 - phi_n / (phi_n + exp(3.535 - 0.02597*phi_n))
    return min(0.99, result)


def calc_phi_N(crop_type):
    if crop_type.bio_N_opt == 0:
        return 300
    else:
        result = 200 * ((crop_type.bio_N/crop_type.bio_N_opt) - 0.5)
        return max(0, result)


def calculate_pstrs(crop_type):
    if crop_type.bio_P_opt == 0:
        return 0
    phi_p = calc_phi_P(crop_type)
    result = 1 - phi_p / (phi_p + exp(3.535 - 0.02597 * phi_p))
    return min(0.99, result)


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
def record_biomass_results(crop_type, time, weather, H_phosyn):
    if time.day == 1 and time.year == 1:
        reset_file(biomass_test_file)

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