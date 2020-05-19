"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_fixation.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating the
             nitrogen fixation data of a crop_type. Currently the only
             function meant to be used outside of this file is the calc_N_fixation()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    fix_nitrogen = boolean indicating whether the crop can fix nitrogen

    z_root = Depth of root development in the soil on a given day

    fr_PHU = Fraction of potential heat units accumulated for the plant on a
             given day in the growing season.

    act_N_up_each_layer = List of actual nitrogen uptakes from each soil layer.
"""


def calc_N_fixation(soil, crop_type):
    """
    Description:
        Calculates the amount of nitrogen added to the plant biomass via fixation.
        Unlike other files in this folder, the functions defined in this file are
        only called for nitrogen fixing crops and are therefore not called from
        crop.py but instead from nitrogen_uptake.py. They should be considered
        helper methods for nitrogen fixing plants
        "pseudocode_crop" C.5.D.1

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class

    Returns:
        float: nitrogen fixated by the crop
    """

    # Check if this crop can form symbiotic nitrogen fixation associations
    if not crop_type.fix_nitrogen:
        return 0
    else:
        accessible_layers = get_root_accessible_layers(soil, crop_type)
        f_gr = calc_f_gr(crop_type)
        f_NO3 = calc_f_NO3(accessible_layers)
        f_sw = calc_f_sw(accessible_layers)
        N_demand = calc_N_demand(crop_type, accessible_layers)

        N_fix = N_demand * f_gr * min(f_sw, f_NO3, 1)

        if N_fix > N_demand:
            N_fix = N_demand

        return N_fix


def get_root_accessible_layers(soil, crop_type):
    """
    Description:
        Determines the soil layer of lowest depth which is accessible to root
        biomass. Returns a list containing all of the soil layers accessible
        to root biomass.
        "pseudocode_crop" C.5.D.8

    Args:
        crop_type
        soil
    Returns:
        layers of the soil profile currently accessible to the roots
    """

    accessible_layers = []

    if crop_type.z_root == 0:
        return accessible_layers

    for layer in soil.soil_layers:
        accessible_layers.append(layer)

        if crop_type.z_root <= layer.bottom_depth:
            break
    return accessible_layers


def calc_f_gr(crop_type):
    """
    Description:
        Calculates growth stage factor.
        "pseudocode_crop" C.5.D.2

    Args:
        crop_type
    Returns:
        float: growth stage factor
    """

    fr_PHU = crop_type.fr_PHU

    if fr_PHU <= 0.15:
        return 0

    elif fr_PHU <= 0.3:
        return 6.67 * fr_PHU - 1

    elif fr_PHU <= 0.55:
        return 1

    elif fr_PHU <= 0.75:
        return 3.75 - 5 * fr_PHU

    else:
        return 0


def calc_f_NO3(accessible_layers):
    """
    Description:
        Calculates soil nitrate factor.
        "pseudocode_crop" C.5.D.3/4

    Args:
        accessible_layers: the root accessible layers (determined in get_root_accessible_layers)
    Returns:
        float: growth stage factor
    """

    # C.5.D.3
    NO3_root = sum([layer.NO3 for layer in accessible_layers])

    # C.5.D.4
    if NO3_root <= 100:
        return 1

    elif NO3_root <= 300:
        return 1.5 - 0.0005 * NO3_root

    else:
        return 0


def calc_f_sw(accessible_layers):
    """
    Description:
        Calculates soil water factor.
        "pseudocode_crop" C.5.D.5/6

    Args:
        accessible_layers
    Returns:
        float: soil water factor
    """

    SW_root = sum([layer.soil_water for layer in accessible_layers])
    FC_root = sum([layer.fc_water for layer in accessible_layers])

    if FC_root == 0:
        return 0

    return SW_root / (0.85 * FC_root)


def calc_N_demand(crop_type, accessible_layers):
    """
    Description:
        Calculates N demand
        "pseudocode_crop" C.5.D.7

    Args:
        crop_type
        accessible_layers
    Returns:
        float: nitrogen demand
    """

    NO3_root = sum([layer.NO3 for layer in accessible_layers])

    pot_N_up_root = sum(crop_type.pot_N_up_each_layer[:len(accessible_layers)])

    N_demand = max(pot_N_up_root - NO3_root, 0)

    return N_demand
