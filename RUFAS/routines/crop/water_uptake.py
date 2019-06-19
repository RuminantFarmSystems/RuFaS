"""
RUFAS: Ruminant Farm Systems Model

File name: water_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil water uptake information of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    soil.Et_max = Maximum plant transpiration on a given day (mm H2O)

    beta_w = Water-use distribution parameter

    epco = Plant uptake compensation factor

    water_uptake_each_layer = Actual plant water uptake for each soil layer

    Et_actual = Actual amount of transpiration that occurs on a given day

    water_actual_up = Total plant water uptake on a given day


CropType values updated by calling update_all():

    water_uptake_each_layer
    water_actual_up
    Et_actual
"""
###############################################################################
from math import exp


#
# This function updates all of a crop's soil water uptake information.
#
def update_all(crop_type, soil, time):
    max_uptakes_ly = calc_max_water_uptake_each_layer(crop_type, soil)

    # First adjustment of water uptakes
    adj_uptakes_ly = inc_lower_layer_uptake(crop_type, soil, max_uptakes_ly)

    # Second adjustment of water uptakes
    adj_uptakes_ly = decrease_effic_of_uptake(soil, adj_uptakes_ly)

    # Calculate total actual water uptake
    calc_act_water_uptake(crop_type, soil, adj_uptakes_ly, time)


#
# Calculates the maximum potential water uptake from each soil layer and
# returns these values in a list ordered shallow to deep. The soil layers
# in soil.listOfSoilLayers should already be in this order.
# "pseudocode_crop" C.4.A
#
def calc_max_water_uptake_each_layer(crop_type, soil):
    upper_boundary_uptake = 0
    max_uptake_each_layer = []

    # 4.A.2
    for layer in soil.listOfSoilLayers:
        lower_boundary_uptake = calc_max_water_uptake_z(crop_type, soil, layer.bottomDepth)
        max_uptake_this_layer = lower_boundary_uptake - upper_boundary_uptake
        max_uptake_each_layer.append(max_uptake_this_layer)

        # update upper boundary for next layer to equal lower of this layer
        upper_boundary_uptake = lower_boundary_uptake

    return max_uptake_each_layer


#
# Calculates potential water uptake from the soil surface to a specified depth
# z (mm H2O).
# "pseudocode_crop" C.4.A.1
#
def calc_max_water_uptake_z(crop_type, soil, z):
    if crop_type.z_root == 0:
        return 0
    else:
        term1 = soil.Et_max / (1 - exp(-1 * crop_type.beta_w))
        term2 = 1 - exp(-1*crop_type.beta_w * z / crop_type.z_root)
        return term1 * term2


#
# In some cases, actual soil water content in layers overlying a layer may not
# be sufficient to meet the potential uptake of those layers as calculated by
# calc_max_water_uptake_each_layer(). In these cases, lower soil layers may be
# allowed to compensate by increasing their potential uptake.
# This function takes in the initially calculated potential uptakes, and returns
# a list of adjusted potential uptakes that compensate for this situation.
# "pseudocode_crop" C.4.B.1/2/3
#
def inc_lower_layer_uptake(crop_type, soil, uptake_each_layer):
    # Sum of potential uptake for layers above current layer
    water_uptake_above = 0

    # Sum of available water for layers above current layer
    water_avail_above = 0

    # Water uptake demand not met by overlying soil layers
    water_demand = 0

    # A list of the adjusted uptakes for each layer
    adjusted_uptakes = []

    # C.4.B.2
    for uptake, layer in zip(uptake_each_layer, soil.listOfSoilLayers):
        adjusted_uptake = uptake + water_demand * crop_type.epco
        adjusted_uptakes.append(adjusted_uptake)

        # C.4.B.3
        # update values for next layer
        water_uptake_above += adjusted_uptake
        water_avail_above += layer.currentSoilWaterMM
        water_demand = water_uptake_above - water_avail_above
        if water_demand < 0:
            water_demand = 0

    return adjusted_uptakes


#
# As water content decreases, the soil holds remaining water more tightly,
# resulting in a decrease in the efficiency of uptake. This function takes in
# a list of potential uptakes, and returns a list of adjusted potential uptakes
# that compensate for this situation.
# "pseudocode_crop" C.4.B.4/5
#
def decrease_effic_of_uptake(soil, uptake_each_layer):
    adjusted_uptakes = []

    for uptake, layer in zip(uptake_each_layer, soil.listOfSoilLayers):
        # Point at which plant available water in soil layer begins to limit
        # efficiency of plant uptake (mm H2O)
        # C.4.B.5
        AWC_limit = 0.25 * (layer.fcWater - layer.wiltingWater) + layer.wiltingWater

        # C.4.B.4
        if layer.currentSoilWaterMM > AWC_limit:
            adjusted_uptakes.append(uptake)
        else:
            inside_exp = 5 * ((layer.currentSoilWaterMM / AWC_limit) - 1)
            adjusted_uptake = uptake * exp(inside_exp)
            adjusted_uptakes.append(adjusted_uptake)

    return adjusted_uptakes


#
# Calculates the actual water uptake by the plant. It uses this value to
# update Et_actual and water_actual_up.
# "pseudocode_crop" C.4.C.2/3
#
def calc_act_water_uptake(crop_type, soil, adj_uptakes, time):
    act_uptake_each_layer = []

    # Calculate actual uptake for each layer
    # C.4.C.1
    for uptake, layer in zip(adj_uptakes, soil.listOfSoilLayers):
        act_uptake = min(uptake, layer.currentSoilWaterMM - layer.wiltingWater)

        layer.Et_actual = act_uptake

        act_uptake_each_layer.append(act_uptake)

    crop_type.water_uptake_each_layer = act_uptake_each_layer

    # Calculate total plant uptake of water from soil profile
    # C.4.C.2
    crop_type.water_actual_up = sum(act_uptake_each_layer)

