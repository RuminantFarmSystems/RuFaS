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

from math import exp, log

from .nitrogen_fixation import calc_N_fixation


def update_all(soil, crop_type):
    """
    Description:
        Updates nitrogen uptake information for the given crop.

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
    """

    calc_fr_N(crop_type)
    calc_bio_N_opt(crop_type)
    calc_N_up(crop_type)
    calc_act_N_up_each_layer(soil, crop_type)
    crop_type.N_act_up = sum(crop_type.act_N_up_each_layer)
    calc_bio_N(soil, crop_type)
    N_uptake(soil)


def calc_fr_N(crop_type):
    """
    Description:
        Calculates the fraction of nitrogen in the plant biomass on a given day.
       "pseudocode_crop" C.5.B.1

    Args:
        crop_type
    """

    n2 = calc_n2(crop_type)
    n1 = calc_n1(crop_type, n2)

    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_N = 0
    else:
        term1 = crop_type.fr_n1 - crop_type.fr_n3

        exp_part = exp(n1 + n2 * crop_type.prev_fr_PHU)
        term2 = 1 - crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part)

        crop_type.fr_N = term1 * term2 + crop_type.fr_n3


def calc_n2(crop_type):
    """
    Description:
        Calculates the second shape coefficient.
       "pseudocode_crop" C.5.A.1

    Args:
        crop_type

    Returns:
        float: second shape coefficient
    """

    term1 = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2
    )

    term2 = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_100, crop_type.fr_n3ish
    )

    term3 = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (term1 - term2) / term3


def calc_n1(crop_type, n2):
    """
    Description:
        Calculates the first shape coefficient.
       "pseudocode_crop" C.5.A.2

    Args:
        crop_type
        n2: the second shape coefficient

    Returns:
        float: the first shape coefficient
    """

    term1 = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2)

    return term1 + n2 * crop_type.fr_PHU_50


def calc_log_term_of_shape_coefficient(crop_type, fr_PHU_frac, fr_nx):
    """
    Description:
        Helper function. Calculates the log term in the shape coefficient calculations
       "pseudocode_crop" C.5.A.2

    Args:
        crop_type
        fr_PHU_frac: the fraction of the fraction of potential heat units
         accumulated
        fr_nx: this function is generalized for calculating the log terms of
         multiple shape coefficient, fr_nx represents the fraction of shape
         coefficient x

    Returns:
        float: log term in the calculations
    """

    bottom = 1 - (fr_nx - crop_type.fr_n3) / (crop_type.fr_n1 - crop_type.fr_n3)
    inside = (fr_PHU_frac / bottom) - fr_PHU_frac

    return log(inside)


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
