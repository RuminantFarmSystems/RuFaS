"""
RUFAS: Ruminant Farm Systems Model

File name: transpiration.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the soil water uptake information of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    soil.trans_max = Maximum plant transpiration on a given day (mm H2O)

    beta_w = Water-use distribution parameter

    epco = Plant uptake compensation factor

    water_uptake_each_layer = Actual plant water uptake for each soil layer

    trans_act = Actual amount of transpiration that occurs on a given day

    water_act_up = Total plant water uptake on a given day


CropType values updated by calling update_all():

    water_uptake_each_layer
    water_act_up
    trans_act
"""

from math import exp


def update_all(soil, crop_type):
    """This function updates all of a crop's soil water uptake information.

    Inputs:
        crop_type
        soil
    """

    max_uptakes_ly = calc_max_water_uptake_each_layer(soil, crop_type)

    # First adjustment of water uptakes
    adj_uptakes_ly = inc_lower_layer_uptake(soil, crop_type, max_uptakes_ly)

    # Second adjustment of water uptakes
    adj_uptakes_ly = decrease_effic_of_uptake(soil, adj_uptakes_ly)

    # Calculate total actual water uptake
    calc_act_water_uptake(soil, crop_type, adj_uptakes_ly)


def calc_max_water_uptake_each_layer(soil, crop_type):
    """Calculates the maximum potential water uptake from each soil layer and
       returns these values in a list ordered shallow to deep. The soil layers
       in soil.soil_layers should already be in this order.
       "pseudocode_crop" C.4.A

    Inputs:
        crop_type
        soil
    Returns:
        list: maximum uptake for each layer
    """

    upper_boundary_uptake = 0
    max_uptake_each_layer = []

    # 4.A.2
    for layer in soil.soil_layers:
        lower_boundary_uptake = calc_max_water_uptake_z(soil, crop_type, layer.bottom_depth)
        max_uptake_this_layer = lower_boundary_uptake - upper_boundary_uptake
        max_uptake_each_layer.append(max_uptake_this_layer)

        # update upper boundary for next layer to equal lower of this layer
        upper_boundary_uptake = lower_boundary_uptake

    return max_uptake_each_layer


def calc_max_water_uptake_z(soil, crop_type, z):
    """Calculates potential water uptake from the soil surface to a specified depth
       z (mm H2O).
       "pseudocode_crop" C.4.A.1

    Inputs:
        crop_type
        soil
        z: a depth
    Returns:
        int: water uptake potential from the surface to a certain depth
    """

    if crop_type.z_root == 0:
        return 0
    else:
        term1 = soil.trans_max / (1 - exp(-1 * crop_type.beta_w))
        term2 = 1 - exp(-1*crop_type.beta_w * z / crop_type.z_root)
        return term1 * term2


def inc_lower_layer_uptake(soil, crop_type, uptake_each_layer):
    """In some cases, actual soil water content in layers overlying a layer may not
       be sufficient to meet the potential uptake of those layers as calculated by
       calc_max_water_uptake_each_layer(). In these cases, lower soil layers may be
       allowed to compensate by increasing their potential uptake.
       This function takes in the initially calculated potential uptakes, and returns
       a list of adjusted potential uptakes that compensate for this situation.
       "pseudocode_crop" C.4.B.1/2/3

    Inputs:
        crop_type
        soil
        uptake_each_layer
    Returns:
        list: uptake values adjusted
    """

    # Sum of potential uptake for layers above current layer
    water_uptake_above = 0

    # Sum of available water for layers above current layer
    water_avail_above = 0

    # Water uptake demand not met by overlying soil layers
    water_demand = 0

    # A list of the adjusted uptakes for each layer
    adjusted_uptakes = []

    # C.4.B.2
    for uptake, layer in zip(uptake_each_layer, soil.soil_layers):
        adjusted_uptake = uptake + water_demand * crop_type.epco
        adjusted_uptakes.append(adjusted_uptake)

        # C.4.B.3
        # update values for next layer
        water_uptake_above += adjusted_uptake
        water_avail_above += layer.soil_water
        water_demand = water_uptake_above - water_avail_above
        if water_demand < 0:
            water_demand = 0

    return adjusted_uptakes


def decrease_effic_of_uptake(soil, uptake_each_layer):
    """As water content decreases, the soil holds remaining water more tightly,
       resulting in a decrease in the efficiency of uptake. This function takes in
       a list of potential uptakes, and returns a list of adjusted potential uptakes
       that compensate for this situation.
       "pseudocode_crop" C.4.B.4/5

    Inputs:
        soil
        uptake_each_layer
    Returns:
        list: uptake values adjusted
    """

    adjusted_uptakes = []

    for uptake, layer in zip(uptake_each_layer, soil.soil_layers):
        # Point at which plant available water in soil layer begins to limit
        # efficiency of plant uptake (mm H2O)
        # C.4.B.5
        AWC_limit = 0.25 * (layer.fc_water - layer.wilting_water)

        # C.4.B.4
        if layer.soil_water > AWC_limit:
            adjusted_uptakes.append(uptake)
        else:
            inside_exp = 5 * ((layer.soil_water / AWC_limit) - 1)
            adjusted_uptake = uptake * exp(inside_exp)
            adjusted_uptakes.append(adjusted_uptake)

    return adjusted_uptakes


def calc_act_water_uptake(soil, crop_type, adjusted_uptakes):
    """Calculates the actual water uptake by the plant. It uses this value to
       update trans_act and water_act_up.
       "pseudocode_crop" C.4.C.2/3

    Inputs:
        crop_type
        soil
        adjusted_uptakes
    Returns:
        int: actual water uptake
    """

    act_uptake_each_layer = []

    # Calculate actual uptake for each layer
    # C.4.C.1
    for uptake, layer in zip(adjusted_uptakes, soil.soil_layers):
        act_uptake = min(uptake, layer.soil_water - layer.wilting_water)

        layer.trans_act = act_uptake

        act_uptake_each_layer.append(act_uptake)

    crop_type.water_uptake_each_layer = act_uptake_each_layer

    # Calculate total plant uptake of water from soil profile
    # C.4.C.2
    crop_type.water_act_up = sum(act_uptake_each_layer)
