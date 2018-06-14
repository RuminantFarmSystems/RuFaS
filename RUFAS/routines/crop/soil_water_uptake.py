'''
RUFAS: Ruminant Farm Systems Model

File name: soil_water_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description:

Variable definitions:


CropType values updated by calling update_all():

'''
###############################################################################
from math import exp


#
#
#
def update_all(crop_type, soil, time):
    max_uptakes_ly = calc_max_water_uptake_each_layer(crop_type, soil)

    # First adjustment of water uptakes
    adj_uptakes_ly = inc_lower_layer_uptake(crop_type, soil, max_uptakes_ly)

    # Second adjustment of water uptakes
    adj_uptakes_ly = decrease_effic_of_uptake(soil, adj_uptakes_ly)

    # Calculate total actual water uptake
    calc_act_water_uptake(crop_type, soil, adj_uptakes_ly)


#
#
#
def calc_max_water_uptake_each_layer(crop_type, soil):
    upper_boundary_uptake = 0
    max_uptake_each_layer = []

    for layer in soil.listOfSoilLayers:
        lower_boundary_uptake = calc_max_water_uptake_z(crop_type, layer.bottomDepth)
        max_uptake_this_layer = lower_boundary_uptake - upper_boundary_uptake
        max_uptake_each_layer.append(max_uptake_this_layer)

        # update upper boundary for next layer
        upper_boundary_uptake = lower_boundary_uptake

    return max_uptake_each_layer


#
#
#
def calc_max_water_uptake_z(crop_type, z):
    term1 = crop_type.E_t  / (1 - exp(-1*crop_type.beta_w))
    term2 = 1 - exp(-1*crop_type.beta_w * z / crop_type.z_root)
    return term1 * term2


#
#
#
def inc_lower_layer_uptake(crop_type, soil, uptake_each_layer):
    water_uptake_above = 0
    water_avail_above = 0
    water_demand = 0
    adjusted_uptakes = []

    for uptake, layer in zip(uptake_each_layer, soil.listOfSoilLayers):
        adjusted_uptake = uptake + water_demand * crop_type.epco
        adjusted_uptakes.append(adjusted_uptake)

        # update values for next layer
        water_uptake_above += adjusted_uptake
        water_avail_above += layer.currentSoilWaterMM
        water_demand = water_uptake_above-water_avail_above
        if water_demand < 0 : water_demand = 0

    return adjusted_uptakes


#
#
#
def decrease_effic_of_uptake(soil, uptake_each_layer):
    adjusted_uptakes = []
    for uptake, layer in zip(uptake_each_layer, soil.listOfSoilLayers):
        AWC = 0.25 * (layer.fcWater - layer.wiltingWater) + layer.wiltingWater

        if layer.currentSoilWaterMM > AWC:
            adjusted_uptakes.append(uptake)
        else:
            inside_exp = 5 * (layer.currentSoilWaterMM / AWC  -  1)
            adjusted_uptake = uptake * exp(inside_exp)
            adjusted_uptakes.append(adjusted_uptake)

    return adjusted_uptakes


#
#
#
def calc_act_water_uptake(crop_type, soil, adj_uptakes):
    act_uptake_each_layer = []
    for uptake, layer in zip(adj_uptakes, soil.listOfSoilLayers):
        act_uptake = min(uptake, layer.currentSoilWaterMM - layer.wiltingWater)
        act_uptake_each_layer.append(act_uptake)

    crop_type.water_uptake_each_layer = act_uptake_each_layer
    crop_type.actual_E_t = sum(act_uptake_each_layer)


#==============================================================================

''' The following can be used for testing purposes '''

#
# The file that will record results of the root depth calculations.
# This is for testing purposes.
#
test_file = "tests/crop_test_files/phosphorus_uptake_results.csv"

#
# The following will record the root depth calculations into the
# test file.
#
def record_results(crop_type, soil, time):
    if time.day == 1 and time.year == 1:
        reset_file((test_file))

    with open(test_file, "a") as resultFile:
        result = "%i,%f,%f,%f,%f,%f,%f,%f,%f,%f\n" % (
            time.day,
            crop_type.biomass_actual,
            crop_type.z_root,
            crop_type.fr_P,
            crop_type.bio_P_opt,
            crop_type.P_up,
            crop_type.act_P_up_each_layer[0],
            crop_type.act_P_up_each_layer[1],
            crop_type.act_P_up_each_layer[2],
            crop_type.bio_P

        )
        if time.day == 1 and time.year == 1:
            resultFile.write("day,biomass_actual,z_root,fr_P,bio_P_opt,P_up,"
                             "actPup1,actPup2,actPup3,bio_P\n")
        resultFile.write(result)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass