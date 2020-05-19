"""
RUFAS: Ruminant Farm Systems Model

File name: phosphorus_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the phosphorus uptake information of a crop_type.
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

CropType attribute definitions:

    fr_p1 = Normal fraction of phosphorus in the plant biomass at emergence

    fr_p2 = Normal fraction of phosphorus in the plant biomass at 50% maturity

    fr_p3 = Normal fraction of phosphorus in the plant biomass at maturity

    fr_p3ish = Normal fraction of phosphorus in the plant biomass near maturity

    fr_P =  Fraction of phosphorus in the plant biomass on a given day

    bio_P_opt = Optimal mass of phosphorus stored in plant material (kg P/ha)

    P_up = Potential phosphorus uptake (kg P/ha)

    beta_p = Phosphorus uptake distribution parameter

    z_root = Depth of soil development on a given day (mm)

    act_P_up_each_layer = List of actual phosphorus uptakes from soil solution
                          in each soil layer.

    P_act_up = Actual amount of phosphorus removed from the soil solution
               on a given day (kg P/ha)

    bio_P = Actual mass of phosphorus stored in plant material (kg P/ha)


CropType values updated by calling update_all():

    fr_P
    bio_P_opt
    P_up
    act_P_up_each_layer
    P_act_up
    bio_P
"""

from math import log, exp


def update_all(soil, crop_type):
    """
    Description:
        Invokes the functions necessary to update phosphorus uptake information
        for the given crop.

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
    """

    calc_fr_P(crop_type)
    calc_bio_P_opt(crop_type)
    calc_P_up(crop_type)
    calc_act_P_up_each_layer(soil, crop_type)
    calc_bio_P(soil, crop_type)


def calc_fr_P(crop_type):
    """
    Description:
        Calculates fraction of phosphorus in the plant biomass.
        "pseudocode_crop" C.6.B.1

    Args:
        crop_type
    """

    p2 = calc_p2(crop_type)
    p1 = calc_p1(crop_type, p2)
    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_P = 0
    else:
        first_term = crop_type.fr_p1 - crop_type.fr_p3

        exp_part = exp(p1 - p2 * crop_type.prev_fr_PHU)
        second_term = 1 - (crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part))

        crop_type.fr_P = first_term * second_term + crop_type.fr_p3


def calc_p2(crop_type):
    """
    Description:
        Calculates the second shape coefficient.
        "pseudocode_crop" C.6.A.1

    Args:
        crop_type

    Returns:
        float: second shape coefficient
    """

    first_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    second_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_100, crop_type.fr_p3ish
    )

    third_term = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (first_term - second_term) / third_term


def calc_p1(crop_type, p2):
    """
    Description:
        Calculates the first shape coefficient.
        "pseudocode_crop" C.6.A.2

    Args:
        crop_type
        p2: second shape coefficient

    Returns:
        float: first shape coefficient
    """

    first_term = calc_log_term_of_shape_coefficient(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    return first_term + p2 * crop_type.fr_PHU_50


def calc_log_term_of_shape_coefficient(crop_type, fr_PHU_frac, fr_px):
    """
    Description:
        Helper function. Calculates the log term in the shape coefficient calculations
        "pseudocode_crop" C.6.A.2

    Args:
        crop_type
        fr_PHU_frac: the fraction of the fraction of potential heat units
        fr_px: this function is used to calculate the log term in the calculations
            of multiple shape coefficients. The fraction of p shape coefficient x

    Returns:
        float: log term in the calculations
    """

    bottom = 1 - (fr_px - crop_type.fr_p3) / (crop_type.fr_p1 - crop_type.fr_p3)
    inside = (fr_PHU_frac / bottom) - fr_PHU_frac
    return log(inside)


def calc_bio_P_opt(crop_type):
    """
    Description:
        Calculates optimal mass of phosphorus stored in plant material.
        "pseudocode_crop" C.6.B.2

    Args:
        crop_type
    """

    crop_type.bio_P_opt = crop_type.prev_biomass_actual * crop_type.fr_P


def calc_P_up(crop_type):
    """
    Description:
        Calculates potential phosphorus uptake.
        "pseudocode_crop" C.6.B.3

    Args:
        crop_type
    """

    if crop_type.bio_P_opt < crop_type.bio_P:
        crop_type.P_up = 0
    else:
        option1 = crop_type.bio_P_opt - crop_type.bio_P
        option2 = 4 * crop_type.fr_p3 * crop_type.d_biomass_max
        crop_type.P_up = 1.5 * min(option1, option2)


def calc_act_P_up_each_layer(soil, crop_type):
    """
    Description:
        Calculates the actual phosphorus uptake from soil solution in each layer.
        Saves the list containing these values to act_P_up_each_layer attribute.
        The order of the values in the list corresponds with the order of the layers
        in soil.soil_layers. The soil layers in that list need to be in order
        of shallowest to deepest for this to work correctly.
        "pseudocode_crop" C.6.C.4-7

    Args:
        soil
        crop_type
    """

    P_up_each_layer = calc_P_up_each_layer(soil, crop_type)

    # Running total of potential phosphorus uptake in overlying layers
    P_up_over = 0

    # Running total of phosphorus content of soil solution in overlying layers
    P_sol_over = 0

    # Phosphorus uptake demand not met in overlying soil layers
    P_demand = 0

    for pot_P_up, layer in zip(P_up_each_layer, soil.soil_layers):
        # C.6.C.4
        act_P_up = min((pot_P_up + P_demand), layer.labile_P)
        # C.6.C.7
        layer.P_uptake = act_P_up

        # C.6.C.6
        # Update values for next layer
        P_up_over += pot_P_up
        P_sol_over += layer.labile_P
        # C.6.C.5
        P_demand = P_up_over - P_sol_over
        if P_demand < 0:
            P_demand = 0


def calc_P_up_each_layer(soil, crop_type):
    """
    Description:
        Calculates the potential phosphorus uptake from soil solution in each layer.
        Returns a list containing these values. The order of the values in the list
        corresponds with the order of the layers in soil.soil_layers. The soil
        layers in that list need to be in order of shallowest to deepest for this
        to work correctly.
        "pseudocode_crop" C.6.C.3

    Args:
        soil
        crop_type
    """

    P_up_each_layer = []
    P_up_for_top_of_layer = 0
    for layer in soil.soil_layers:
        P_up_for_bottom_of_layer = calc_P_up_z(crop_type, layer.bottom_depth)
        P_up_ly = P_up_for_bottom_of_layer - P_up_for_top_of_layer

        P_up_each_layer.append(P_up_ly)

        # Set the top for next layer equal to bottom of this layer
        P_up_for_top_of_layer = P_up_for_bottom_of_layer

    return P_up_each_layer


def calc_P_up_z(crop_type, z):
    """
    Description:
        Calculates potential phosphorus uptake from soil solution at the surface to
        depth z. This function is used in calc_P_up_each_layer.
        "pseudocode_crop" C.6.C.1

    Args:
        crop_type
        z: the given depth

    Returns:
        float: nitrogen uptake from the surface to a depth
    """

    if crop_type.z_root == 0:
        return 0
    term1 = crop_type.P_up / (1 - exp(-1 * crop_type.beta_p))
    term2 = 1 - exp(-1 * crop_type.beta_p * z / crop_type.z_root)
    return term1 * term2


def calc_bio_P(soil, crop_type):
    """
    Description:
        Calculates actual mass of phosphorus stored in plant material.

    Args:
        crop_type
        soil
    """

    for layer in soil.soil_layers:
        crop_type.bio_P += layer.P_uptake
