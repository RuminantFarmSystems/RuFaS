'''
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_fixation.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating the
             nitrogen fixation data of a crop_type. Currently the only
             function meant to be used outside of this file is the calc_N_fixation()
             function. The other functions are meant to serve as helper
             functions within this file.

Variable definitions:


CropType values updated by calling update_all():

'''
###############################################################################

#
# Calculates the amount of nitrogen added to the plant biomass by fixation.
# "Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.6
#
def calc_N_fixation(crop_type, soil):
    # Check if this crop can form symbiotic nitrogen fixation associations
    if not crop_type.fix_nitrogen:
        return 0
    else:
        accessible_layers = get_root_accessible_layers(crop_type, soil)
        f_gr = calc_f_gr(crop_type)
        f_NO3 = calc_f_NO3(accessible_layers)
        f_sw = calc_f_sw(accessible_layers)
        N_demand = calc_N_demand(crop_type, accessible_layers)

        return N_demand * f_gr * min(f_sw, f_NO3, 1)


#
# Determines the soil layer of lowest depth that is accessible to root
# biomass. Returns a list containing all of the soil layers accessible
# to root biomass.
# "Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.1
#
def get_root_accessible_layers(crop_type, soil):
    accessible_layers = []

    if crop_type.z_root == 0:
        return accessible_layers

    for soilLayer in soil.listOfSoilLayers:
        accessible_layers.append(soilLayer)

        if crop_type.z_root <= soilLayer.bottomDepth:
            break
    return accessible_layers


#
# Calculates growth stage factor.
# "Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.2
#
def calc_f_gr(crop_type):
    fr_PHU = crop_type.fr_PHU

    if fr_PHU <= 0.15: return 0

    elif fr_PHU <= 0.3: return 6.67 * fr_PHU - 1

    elif fr_PHU <= 0.55: return 1

    elif fr_PHU <= 0.75: return 3.75 - 5 * fr_PHU

    else: return 0


#
# Calculates soil nitrate factor.
# "Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.3
#
def calc_f_NO3(accessible_layers):
    NO3_root = sum([layer.NO3 for layer in accessible_layers])

    if NO3_root <= 100: return 1

    elif NO3_root <= 300: return 1.5 - 0.0005 * NO3_root

    else: return 0


#
# Calculates soil water factor.
# "Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.4
#
def calc_f_sw(accessible_layers):
    SW_root = sum([layer.currentSoilWaterMM for layer in accessible_layers])
    FC_root = sum([layer.fcWater for layer in accessible_layers])

    if FC_root == 0:
        return 0

    return SW_root / (0.85 * FC_root)


#
# Calculates N demand
#"Pseudo code_SC_NitrogenUptake_1.0.docx" section 3.D.5
#
def calc_N_demand(crop_type, accessible_layers):
    NO3_root = sum([layer.NO3 for layer in accessible_layers])

    count_accessible = len(accessible_layers)
    act_N_up_root = sum(crop_type.act_N_up_each_layer[:count_accessible])

    return act_N_up_root - NO3_root


#==============================================================================

''' The following can be used for testing purposes '''

#
# The file that will record results of the root depth calculations.
# This is for testing purposes.
#
test_file = "tests/crop_test_files/nitrogen_uptake_results.csv"

#
# The following will record the root depth calculations into the
# test file.
#
def record_results(crop_type, time):
    if time.day == 1 and time.year == 1:
        reset_file((test_file))

    with open(test_file, "a") as resultFile:
        result = "%i,%f,%f,%f,%f\n" % (
            time.day,
            crop_type.prev_biomass_actual,
            crop_type.fr_N,
            crop_type.bio_N_opt,
            crop_type.N_up
        )
        if time.day == 1 and time.year == 1:
            resultFile.write("day,prev_biomass_actual,fr_N,bio_N_opt,N_up\n")
        resultFile.write(result)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass