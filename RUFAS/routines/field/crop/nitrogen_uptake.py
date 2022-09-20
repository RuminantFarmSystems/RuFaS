"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the nitrogen uptake information of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    fr_n1 = Normal fraction of nitrogen in the plant biomass at emergence

    fr_n2 = Normal fraction of nitrogen in the plant biomass at 50% maturity

    fr_n3 = Normal fraction of nitrogen in the plant biomass at maturity

    fr_n3ish = Normal fraction of nitrogen in the plant biomass near maturity

    fr_N = Fraction of nitrogen in the plant biomass on a given day

    bio_N_opt = Optimal mass of nitrogen stored in plant biomass (kg N/ha)

    N_up = Potential nitrogen uptake (kg N/ha)

    beta_n = Nitrogen uptake distribution parameter

    act_N_up_each_layer = List of actual nitrogen uptakes from each soil layer.

    N_act_up = Actual amount of nitrogen removed from the soil solution
                  on a given day (kg N/ha)

    bio_N = Actual mass of nitrogen stored in plant material (kg N/ha)


CropType values updated by calling update_all():

    fr_N
    bio_N_opt
    N_up
    act_N_up_each_layer
    N_act_up
    bio_N
"""

from math import log, exp
from RUFAS.routines.field.crop.nitrogen_fixation import calc_N_fixation

# TODO: These functions should probably be moved to the base_crop class as member functions

def update_all(soil, crop_type):
    """
    Description:
        Updates nitrogen uptake information for the given crop.

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
    """

    update_nfrac(crop_type)
    calc_bio_N_opt(crop_type)
    calc_N_up(crop_type)
    calc_act_N_up_each_layer(soil, crop_type)
    crop_type.N_act_up = sum(crop_type.act_N_up_each_layer)
    calc_bio_N(soil, crop_type)
    N_uptake(soil)


def calc_nfrac(phu_frac: float, nfrac_1: float, nfrac_3: float, shape1:float, shape2:float) -> float:
    """
    Description:
        Calculates the fraction of nitrogen in the plant biomass on a given day.
       "pseudocode_crop" C.5.B.1

    Args:
        phu_frac: the fraction of total PHU accumulated to date
        nfrac_1: the fraction nitrogen in the biomass at stage 1
        nfrac_3: the fraction nitrogen in the biomass at stage 3
        shape1: first shape parameter
        shape2: second shape parameter
    """

    ndiff = nfrac_1 - nfrac_3
    e_term = exp(shape1 + (shape2 * phu_frac))
    brackies = 1 - (phu_frac / (phu_frac + e_term))
    return (ndiff * brackies) + nfrac_3


    ## TODO: This used to be calculated from the **previous** day's values but I don't understand why. - Clay
    # shape2 = calc_nshape2(heatfrac_half, heatfrac_full, nfrac_1, nfrac_2, nfrac_near, nfrac_3)
    # shape1 = calc_nshape1(heatfrac_half, nfrac_2, nfrac_1, nfrac_3)
    #
    # if crop_type.prev_biomass_actual == 0:
    #     crop_type.fr_N = 0
    # else:
    #     term1 = crop_type.fr_n1 - crop_type.fr_n3
    #
    #     exp_part = exp(n1 + n2 * crop_type.prev_fr_PHU)
    #     term2 = 1 - crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part)
    #
    #     crop_type.fr_N = term1 * term2 + crop_type.fr_n3


def update_nfrac(crop) -> None:
    """
    Description: update a crop's nitrogen fraction

    Args:
        crop: an instance of BaseCrop

    Returns: Nothing. Instead, the crop.fr_N attribute is updated.
    """
    shapes = calc_nshapes(heatfrac_half=crop.fr_PHU_50, heatfrac_full=crop.fr_PHU_100, nfrac_1=crop.fr_n1,
                          nfrac_2=crop.fr_n2, nfrac_near=crop.fr_n3ish ,nfrac_3=crop.fr_n3)
    # TODO: using current PHU instead of previous
    if crop.biomass_actual == 0:
        crop.fr_N = 0
    else:
        crop.fr_N = calc_nfrac(phu_frac=crop.fr_PHU, nfrac_1=crop.fr_n3, nfrac_3=crop.fr_n3,
                               shape1=shapes[0], shape2=shapes[1])

def calc_nshapes(heatfrac_half: float, heatfrac_full: float, nfrac_1: float, nfrac_2: float,
                 nfrac_near: float, nfrac_3: float) -> list[float]:
    """
    Description:
        Calculates the shape coefficient for nitrogen fraction.
       "pseudocode_crop" C.5.A.1

    Args:
        heatfrac_half: the fraction of potential heat units at half maturity
        heatfrac_full: the fraction of potential heat units at full maturity
        nfrac_1: the fraction nitrogen in the biomass at stage 1
        nfrac_2: the fraction nitrogen in the biomass at stage 2
        nfrac_near: the fraction nitrogen in the biomass near maturity (stage 3)
        nfrac_3: the fraction nitrogen in the biomass at stage 3
        shape2: the second shape coefficient

    Returns:
        a list of the first and second shape coefficients
    """

    if heatfrac_full == heatfrac_half:  # leads to divide by 0
        raise ValueError("heatfrac_half must not equal heatfrac_full")

    # 1st shape parameter
    log_half = calc_shape_log(heat_frac=heatfrac_half, nfrac_x=nfrac_2, nfrac_3=nfrac_3, nfrac_1=nfrac_1)
    log_full = calc_shape_log(heat_frac=heatfrac_full, nfrac_x=nfrac_near, nfrac_3=nfrac_3, nfrac_1=nfrac_1)
    s2 = (log_half - log_full) / (heatfrac_full - heatfrac_half)

    # second shape parameter
    log_term = calc_shape_log(heat_frac=heatfrac_half, nfrac_x=nfrac_2, nfrac_1=nfrac_1, nfrac_3=nfrac_3)
    s1 = log_term + s2 * heatfrac_half
    return [s1, s2]


def calc_shape_log(heat_frac:float, nfrac_x:float, nfrac_3:float, nfrac_1:float) -> float:
    """
    Description:
    Calculate the log component of shape coefficient formulae
    "pseudocode_crop" C.5.A.2

    Args:
        heat_frac: the fraction of potential heat units of interest
        nfrac_x: the fraction of biomass that is nitrogen at the stage of interest
        nfrac_3: the fraction of nitrogen at maturity
        nfrac_1: the fraction of nitrogen at emergence

    Returns:
        the log term of shape coefficient formula
    """

    # throw an error if any parameters do not satisfy [0-1]
    frac_error_msg = "nfrac_x, heat_frac, nfrac_3, and nfrac_1 must all be between 0 and 1"
    if nfrac_x < 0 or nfrac_x > 1 or heat_frac < 0 or heat_frac > 1 or nfrac_3 < 0 or nfrac_3 > 1 \
            or nfrac_1 < 0 or nfrac_1 > 1:
        raise ValueError(frac_error_msg)

    # raise other errors # TODO: perhaps rather than throwing errors, we should set values to sensible edge case?
    if nfrac_1 <= nfrac_3:  # leads to division by zero or ln(-x)
        raise ValueError("nfrac_1 must be less than nfrac_3")

    if nfrac_x > nfrac_1 or nfrac_x == nfrac_1: # leads to ln(-x) or divide by 0
        raise ValueError("nfrac_x must be less than nfrac_1")

    if nfrac_x == 0: # leads to ln(0)
        raise ValueError("nfrac_x must be greater than 0")
    if heat_frac == 0:
        raise ValueError("heat_x must be greater than 0")

    # calculate results
    denominator = 1 - ((nfrac_x - nfrac_3) / (nfrac_1 - nfrac_3))
    return log((heat_frac / denominator) - heat_frac)

def calc_bio_N_opt(crop_type):
    """
    Description:
        Calculates the optimal mass of nitrogen stored in plant biomass.
       "pseudocode_crop" C.5.B.2

    Args:
        crop_type
    """

    crop_type.bio_N_opt = crop_type.fr_N * crop_type.biomass_actual


def calc_N_up(crop_type):
    """
    Description:
        Calculates potential nitrogen uptake.
       "pseudocode_crop" C.5.B.3

    Args:
        crop_type
    """

    if crop_type.bio_N_opt - crop_type.bio_N < 0:
        crop_type.N_up = 0
    else:
        option1 = crop_type.bio_N_opt - crop_type.bio_N
        option2 = 4 * crop_type.fr_n3 * crop_type.d_biomass_max

        crop_type.N_up = min(option1, option2)


def calc_act_N_up_each_layer(soil, crop_type):
    """
    Description:
        Calculates the actual nitrogen uptake from soil solution in each layer.
        Saves the list containing these values to act_N_up_each_layer attribute.
        The order of the values in the list corresponds with the order of the
        layers in soil.soil_layers. The soil layers in that list need to be in
        order of shallowest to deepest for this to work correctly.
        "pseudocode_crop" C.5.C.4/5/6/7

    Args:
        crop_type
        soil
    """

    crop_type.pot_N_up_each_layer = calc_N_up_each_layer(soil, crop_type)
    act_N_up_each_layer = []

    # Running total of potential nitrogen uptake in overlying layers
    N_up_over = 0

    # Running total of nitrate in overlying soil layers
    NO3_over = 0

    # Nitrogen uptake demand not met in overlying soil layers
    N_demand = 0

    for pot_N_up, soil_layer in zip(crop_type.pot_N_up_each_layer, soil.soil_layers):

        # C.5.C.4
        act_N_up = min((pot_N_up + N_demand), soil_layer.NO3)

        # C.5.C.7
        soil_layer.N_uptake = act_N_up
        act_N_up_each_layer.append(act_N_up)

        # Update values so ready for the next layer
        N_up_over += pot_N_up

        # C.5.C.6
        NO3_over += soil_layer.NO3

        # C.5.C.5
        N_demand = max(N_up_over - NO3_over, 0)

        if N_demand < 0:
            N_demand = 0

    crop_type.act_N_up_each_layer = act_N_up_each_layer


def N_uptake(soil):
    for layer in soil.soil_layers:
        layer.NO3 -= layer.N_uptake


def calc_N_up_each_layer(soil, crop_type):
    """
    Description:
        Calculates the potential nitrogen uptake from soil solution in each
        layer. Returns a list containing these values. The order of the values
        in the list corresponds with the order of the layers in
        soil.soil_layers. The soil layers in that list need to be in order of
        shallowest to deepest for this to work correctly.
       "pseudocode_crop" C.5.C.2/3

    Args:
        soil
        crop_type

    Returns:
        list: nitrogen uptake per layer
    """

    N_up_each_layer = []

    N_up_for_top_of_layer = 0
    for layer in soil.soil_layers:
        N_up_for_bottom_of_layer = calc_N_up_z(crop_type, layer.bottom_depth)

        # C.5.C.3
        N_up_ly = N_up_for_bottom_of_layer - N_up_for_top_of_layer

        N_up_each_layer.append(N_up_ly)

        # Set the top for next layer equal to bottom of this layer
        N_up_for_top_of_layer = N_up_for_bottom_of_layer

    return N_up_each_layer


def calc_N_up_z(crop_type, z):
    """
    Description:
        Calculates potential nitrogen uptake from soil solution at the surface
        to depth z. This function is used in calc_N_up_each_layer.
        "pseudocode_crop" C.5.C.1

    Args:
        crop_type
        z: the given depth

    Returns:
        float: nitrogen uptake from the surface to a depth
    """

    if crop_type.z_root == 0:
        return 0
    term1 = crop_type.N_up / (1 - exp(-1 * crop_type.beta_n))
    term2 = 1 - exp(-1 * crop_type.beta_n * z / crop_type.z_root)
    return term1 * term2


def calc_bio_N(soil, crop_type):
    """
    Description:
        Calculates actual mass of nitrogen stored in plant material.
        "pseudocode_crop" C.5.E.1

    Args:
        soil
        crop_type
    """

    crop_type.N_fix = calc_N_fixation(soil, crop_type)
    crop_type.bio_N = crop_type.bio_N + crop_type.N_act_up + crop_type.N_fix
