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

    is_nitrogen_fixer = boolean indicating whether the crop can fix nitrogen

    z_root = Depth of root development in the soil on a given day

    fr_PHU = Fraction of potential heat units accumulated for the plant on a
             given day in the growing season.

    act_N_up_each_layer = List of actual nitrogen uptakes from each soil layer.
"""

from bisect import bisect
# from RUFAS.routines.field.crop.nitrogen_uptake import calc_layer_nitrogen_demand


def calc_fixed_nitrogen(demand, growth_factor, water_factor, nitrate_factor):  # pseudocode C.5.D.1
    """
    Description: calculates the amount of nitrogen added to the plant biomass via fixation

    Args:
        demand: total plant nitrogen demand
        growth_factor: growth stage factor of the plant
        water_factor: soil water factor
        nitrate_factor: soil nitrate factor

    Returns: nitrogen fixed by the crop
    """
    fixed = demand * growth_factor * min(water_factor, nitrate_factor, 1)
    if fixed < demand:
        return demand
    else:
        return fixed


def fix_nitrogen(crop, soil) -> None:
    # TODO: this function needs updating once nitrogen_fixation.py is refactored
    # accessible resources TODO: (should be own function)
    layer_bounds = [layer.bottom_depth for layer in soil.soil_layers]
    deepest_layer = get_root_accessible_layer(crop.z_root, layer_bounds=layer_bounds)
    accessible_layers = [layer for layer in soil.soil_layers[slice(deepest_layer)]]
    accessible_water = sum([layer.soil_water for layer in accessible_layers])
    at_capacity_water = sum([layer.fc_water for layer in accessible_layers])
    accessible_nitrates = sum(layer.NO3 for layer in accessible_layers)

    ## TODO -- this all needs incorporating into Soil and Crop
    # demand = calc_layer_nitrogen_demand(uptake_potentials=, nitrate_availabilities=)
    demand = calc_N_demand(crop, accessible_layers)

    growth_factor = calc_growth_stage_factor(heatfrac=crop.fr_PHU)
    water_factor = calc_soil_water_factor(accessible_water, at_capacity_water)
    nitrate_factor = calc_nitrate_factor(accessible_nitrates)

    crop.N_fix = calc_fixed_nitrogen(demand, growth_factor, water_factor, nitrate_factor)


def get_root_accessible_layer(root_depth: float, layer_bounds: list[float]):  # pseudocode: C.5.D.8
    """
    Description:
        Determines the deepest soil layer that is accessible to root biomass.

    Args:
        root_depth: the root depth of a plant
        layer_bounds: the depths of the lower boundaries of each soil layer

    Returns:
        an integer indicating the deepest soil layer that the roots can access
    """

    if root_depth <= 0:  # handle no roots
        return None
    else:
        deepest_layer = bisect(layer_bounds, root_depth)
        if deepest_layer >= len(layer_bounds) - 1:  # handle roots deeper than soil
            deepest_layer = len(layer_bounds) - 1  # TODO: this should probably be handled differently. but how?
            Warning("root_depth is deeper than the lowest soil layer")
        return deepest_layer


def calc_growth_stage_factor(heatfrac: float) -> float:  # pseudocode C.5.D.2
    """
    Description: calculates plant growth stage factor

    Args:
        heatfrac: the accumulated fraction of potential heat units

    Returns: growth stage factor
    """
    if heatfrac <= 0.15:
        return 0

    elif heatfrac <= 0.3:
        return (6.67 * heatfrac) - 1

    elif heatfrac <= 0.55:
        return 1

    elif heatfrac <= 0.75:
        return 3.75 - (5 * heatfrac)
    else:
        return 0


def calc_nitrate_factor(accessible_nitrates):  # pseudocode: C.5.4
    """
    Description: calculates soil nitrate factor

    Args:
        accessible_nitrates: total nitrates available in the soil layers accessible to roots

    Returns: the nitrate factor
    """
    if accessible_nitrates <= 100:
        return 1
    elif accessible_nitrates <= 300:
        return 1.5 - (0.0005 * accessible_nitrates)
    else:
        return 0


def calc_soil_water_factor(accessible_water: float, at_capacity_water: float) -> float:  # pseudocode: C.5.D.5
    """
    Description: calculates soil water factor

    Args:
        accessible_water: the water content accessible to root biomass
        at_capacity_water: the water accessible at field capacity

    Returns: soil water factor
    """
    return accessible_water / 0.85 * at_capacity_water


def calc_N_demand(crop_type, accessible_layers):  # TODO: why is this different from demand calculated by calc_layer_nitrogen_demand()?
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
