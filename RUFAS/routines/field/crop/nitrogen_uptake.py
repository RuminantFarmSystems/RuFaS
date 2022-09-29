"""
Author(s): Clay Morrow (morrowcj@outlook.com); Andy Achenreiner (achenreiner@wisc.edu)

Description: This module contains the necessary functions for calculating and
             updating the nitrogen uptake information of a crop_type. Currently, the only
             function meant to be used outside this file is the reallocate_nitrogen()
             function. The other functions are meant to serve as helper
             functions within this file.
"""

from math import log, exp
from RUFAS.routines.field.crop.nitrogen_fixation import calc_N_fixation


def reallocate_nitrogen(crop, soil) -> None:
    """
    Description: updates nitrogen uptake information for the given crop (and soil) during the daily growth cycle

    Args:
        crop: an instance of a crop class for which nitrogen should be updated
        soil: an instance of a soil class, from which to draw nitrogen
    """
    update_nitrogen_fraction(crop)
    update_optimal_nitrogen(crop)
    update_potential_nitrogen_uptake(crop)
    uptake_nitrogen(crop, soil)
    fix_nitrogen(crop, soil)
    store_nitrogen_biomass(crop)


def calc_nitrogen_fraction(phu_frac: float, nfrac_1: float, nfrac_3: float, shape1: float, shape2: float) -> float:  # pseudocode: C.5.B.1
    """
    Description: calculates the fraction of nitrogen in the plant biomass on a given day

    Args:
        phu_frac: the fraction of total PHU (PHU fraction) accumulated to date
        nfrac_1: the expected fraction of plant biomass comprised of nitrogen (nitrogen fraction) at emergence
        nfrac_3: the nitrogen fraction at maturity
        shape1: first nitrogen uptake shape parameter
        shape2: second nitrogen uptake shape parameter
    """
    ndiff = nfrac_1 - nfrac_3
    e_term = exp(shape1 + (shape2 * phu_frac))
    brackies = 1 - (phu_frac / (phu_frac + e_term))
    return (ndiff * brackies) + nfrac_3


def update_nitrogen_fraction(crop) -> None:
    """
    Description: update a crop's nitrogen fraction

    Args:
        crop: an instance of BaseCrop

    Returns: Nothing. Instead, the crop.fr_N attribute is updated.
    """
    shapes = calc_shape_parameters(heatfrac_half=crop.fr_PHU_50, heatfrac_full=crop.fr_PHU_100, nfrac_1=crop.fr_n1,
                                   nfrac_2=crop.fr_n2, nfrac_near=crop.fr_n3ish, nfrac_3=crop.fr_n3)
    if crop.biomass_actual == 0:
        crop.fr_N = 0
    else:
        crop.fr_N = calc_nitrogen_fraction(phu_frac=crop.prev_fr_PHU, nfrac_1=crop.fr_n1, nfrac_3=crop.fr_n3,
                                           shape1=shapes[0], shape2=shapes[1])


def calc_shape_parameters(heatfrac_half: float, heatfrac_full: float, nfrac_1: float, nfrac_2: float,
                          nfrac_near: float, nfrac_3: float) -> list[float]:  # pseudocode: C.5.A.1, C.5.A.2
    """
    Description: calculates the shape coefficient for nitrogen fraction

    Args:
        heatfrac_half: the PHU fraction halfway to maturity
        heatfrac_full: the PHU fraction at full maturity
        nfrac_1: the nitrogen fraction at emergence
        nfrac_2: the nitrogen fraction after emergence
        nfrac_near: the nitrogen fraction *near* maturity
        nfrac_3: the nitrogen fraction *at* maturity

    Returns: a list of the first and second shape coefficients
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


def calc_shape_log(heat_frac: float, nfrac_x: float, nfrac_3: float, nfrac_1: float) -> float:  # pseudocode: C.5.A.1, C.5.A.2
    """
    Description: calculate the log component of shape coefficient formulae

    Args:
        heat_frac: the PHU fraction of interest
        nfrac_x: the nitrogen fraction at the developmental stage of interest
        nfrac_3: the nitrogen fraction at maturity
        nfrac_1: the nitrogen fraction at emergence

    Returns: the log term of shape coefficient
    """
    # throw an error if any parameters do not satisfy [0-1]
    frac_error_msg = "nfrac_x, heat_frac, nfrac_3, and nfrac_1 must all be between 0 and 1"
    if nfrac_x < 0 or nfrac_x > 1 or heat_frac < 0 or heat_frac > 1 or nfrac_3 < 0 or nfrac_3 > 1 \
            or nfrac_1 < 0 or nfrac_1 > 1:
        raise ValueError(frac_error_msg)
    # raise other errors  # TODO: perhaps rather than throwing errors, we should set values to sensible edge case?
    if nfrac_1 == nfrac_3:  # leads to divide by zero
        raise ValueError("nfrac_1 must not be equivalent to nfrac_3")
    if nfrac_x == nfrac_1:  # leads to divide by zero
        raise ValueError("nfrac_x must not be equivalent to nfrac_1")
    if nfrac_x == nfrac_3:  # leads to log(0)
        raise ValueError("nfrac_x must not be equivalent to nfrac_3")
    if nfrac_x > nfrac_1 or nfrac_x == nfrac_1:  # leads to ln(-y) or divide by 0
        raise ValueError("nfrac_x must be less than nfrac_1")
    if nfrac_x == 0:  # leads to ln(0)
        raise ValueError("nfrac_x must be greater than 0")
    if heat_frac == 0:
        raise ValueError("heat_x must be greater than 0")
    # calculate first component of formula
    denominator = 1 - ((nfrac_x - nfrac_3) / (nfrac_1 - nfrac_3))
    # additional check
    if denominator > 1:  # leads to log(-y)
        raise ValueError("the quantity (nfrac_x-nfrac_3)/(nfrac_1-nfrac_3) is negative." +
                         "\nIs nfrac_x < nfrac_3 or nfrac_1 < nfrac_3?")
    # final results
    return log((heat_frac / denominator) - heat_frac)


def calc_optimal_nitrogen(nfrac: float, biomass: float) -> float:  # pseudocode: C.5.B.2
    """
    Description: calculates the optimal mass of nitrogen stored in plant biomass

    Args:
        nfrac: the current nitrogen fraction
        biomass: the current plant biomass

    Returns: the optimal nitrogen mass
    """
    return nfrac * biomass


def update_optimal_nitrogen(crop) -> None:
    """
    Description: updates a crops optimal nitrogen based on its current biomass and nitrogen fraction

    Args:
        crop: an instance of a BaseCrop object

    Returns: Nothing. Instead, crop.bio_N_opt is updated
    """
    crop.bio_N_opt = calc_optimal_nitrogen(nfrac=crop.fr_N, biomass=crop.biomass_actual)


def calc_potential_nitrogen_uptake(demand: float, nitrogen_start: float, mature_nfrac: float,
                                   max_growth: float) -> float:  # pseudocode: C.5.B.3
    """
    Description: calculates potential nitrogen uptake for a given day

    Args:
        demand: the maximum potential nitrogen uptake of the plant on a given day
        nitrogen_start: the actual biomass of nitrogen in the plant at the end of the previous day
        mature_nfrac:, the nitrogen fraction of the plant at maturity
        max_growth: the maximum potential biomass the plant can gain on a given day

    Returns: the potential nitrogen uptake for the day
    """
    return min(demand - nitrogen_start, 4 * mature_nfrac * max_growth)


def update_potential_nitrogen_uptake(crop) -> None:
    """
    Description: update a plant's potential nitrogen uptake

    Args:
        crop: an instance of the BaseCrop class

    Returns: Nothing. Instead, updates crop.N_up
    """
    if crop.bio_N_opt - crop.bio_N < 0:
        crop.N_up = 0
    else:
        crop.N_up = calc_potential_nitrogen_uptake(demand=crop.bio_N_opt, nitrogen_start=crop.bio_N,
                                                   mature_nfrac=crop.fr_n3, max_growth=crop.d_biomass_max)


def calc_layer_nitrogen_uptake(layer_demand: list[float], layer_potential: list[float],
                               layer_nitrate: list[float]) -> list[float]:  # pseudocode: C.5.C.4
    """
    Description: calculates the actual nitrogen uptake from each layer of soil

    Args:
        layer_demand: a list of nitrogen demands from each soil layer not by the above layers
        layer_potential: a list of maximum potential nitrogen uptakes from each soil layer
        layer_nitrate: a list of nitrate amounts present in each soil layer

    Returns: a list of the actual nitrogen taken up from each soil layer
    """
    # ensure all list inputs are the same length
    if len(layer_potential) != len(layer_demand) or len(layer_potential) != len(layer_nitrate):
        raise ValueError("layer_potential, layer_demand, and layer_nitrate must be the same length")
    # calculate results
    layer_desired = [potential + demand for potential, demand in zip(layer_potential, layer_demand)]
    return [min(desired, nitrate) for desired, nitrate in zip(layer_desired, layer_nitrate)]


def calc_layer_nitrogen_demand(uptake_potentials: list[float], nitrate_availabilities: list[float]) -> list[float]:  # pseudocode: C.5.C.5
    """
    Description: calculates the nitrogen demand of the plant from each soil layer

    Args:
        uptake_potentials: the maximum potential nitrogen uptake by the plant from each soil layer
        nitrate_availabilities: the available nitrates (NO3) in each soil layer

    Returns: a list of nitrogen demands from each soil layer
    """
    layer_delta = [desired - available for desired, available in zip(uptake_potentials, nitrate_availabilities)]
    layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))]  # cumulative sum, starting at 0
    return [max(val, 0) for val in layer_demand]  # results constrained to zero


def uptake_nitrogen(crop, soil) -> None:
    """
    Description: uptake nitrogen from the soil and reallocate it into the crop

    Args:
        crop: an instance of the BaseCrop class
        soil: an instance of the Soil class, from which nitrogen will be transferred

    Returns:
        Nothing. Instead, nitrogen attributes are updated in crop and soil
    """
    # pre-uptake conditions
    layer_bounds = [layer.bottom_depth for layer in soil.soil_layers]
    layer_nitrates = [layer.NO3 for layer in soil.soil_layers]
    # calculate layer values
    potentials = calc_layer_nitrogen_potential(boundaries=layer_bounds, demand=crop.N_up, root_depth=crop.z_root,
                                               ndistro=crop.beta_n)
    demands = calc_layer_nitrogen_demand(uptake_potentials=potentials, nitrate_availabilities=layer_nitrates)
    uptakes = calc_layer_nitrogen_uptake(layer_demand=demands, layer_potential=potentials, layer_nitrate=layer_nitrates)
    # update attributes
    crop.pot_N_up_each_layer = potentials  # todo: needed?
    crop.act_N_up_each_layer = uptakes  # todo: needed?
    for uptake, layer in zip(uptakes, soil.soil_layers):
        layer.N_uptake = uptake
        layer.NO3 -= uptake  # remove from soil
    crop.N_act_up = sum(uptakes)  # give to crop


def calc_layer_nitrogen_potential(boundaries: list[float], demand: float,
                                  root_depth: float, ndistro: float) -> list[float]:  # pseudocode: C.5.C.2, C.5.C.3
    """
    Description: calculates the potential nitrogen uptake from each soil layer

    Args:
        boundaries: a list of depths of the lower boundaries for each soil layer; must be in ascending order
            (increasing depths)
        demand: the total nitrogen demand of the plant
        root_depth: the current depth of the plant roots
        ndistro: the nitrogen uptake distribution parameter

    Returns: a list of potential nitrogen uptake from each layer
    """
    # check that boundaries are in ascending order
    sorted_boundaries = boundaries.copy()
    sorted_boundaries.sort()
    if sorted_boundaries != boundaries:
        raise ValueError("boundaries must be in ascending order (deeper layers follow shallower ones)")
    # check that there aren't duplicates (each layer should have a unique depth)
    if len(boundaries) != len(set(boundaries)):
        raise ValueError("multiple soil boundaries cannot have the same depths. Remove the redundant layer?")
    # calculate results
    boundary_nitrogen = [calc_nitrogen_uptake_to_depth(demand, x, root_depth, ndistro) for x in boundaries]  # N at each boundary
    boundary_nitrogen.insert(0, 0)  # 0 N uptake at soil surface
    layer_nitrogen = [below - above for below, above in zip(boundary_nitrogen[1:], boundary_nitrogen)]  # subtract previous layer
    return layer_nitrogen


def calc_nitrogen_uptake_to_depth(demand: float, depth: float, root_depth: float, ndistro: float) -> float:  # pseudocode: C.5.C.1
    """
    Description: calculates potential nitrogen uptake from the soil surface to a specified depth

    Args:
        demand: the current nitrogen demand
        depth: the depth to which nitrogen uptake is calculated
        root_depth: the current root depth
        ndistro: the nitrogen uptake distribution parameter

    Returns: the potential amount of nitrogen taken up
    """
    # error checks
    if ndistro == 0:
        raise ValueError("ndistro cannot equal 0")
    # calculate results
    if root_depth <= 0:
        return 0
    else:
        first_term = demand / (1 - exp(-ndistro))
        second_term = 1 - exp(-ndistro * (depth / root_depth))
        return first_term * second_term


def calc_stored_nitrogen(uptake: float, previous: float, fixed: float = 0) -> float:  # C.5.E.1
    """
    Description: calculates nitrogen mass stored in plant material after the current day's growth cycle

    Args:
        uptake: the mass of the nitrogen taken up by the plant on the current day
        previous: the nitrogen mass stored in the plant at the end of the previous day
        fixed: the mass of nitrogen fixed by the plant on the current day

    Returns: the total mass of nitrogen in the plant at the end of current day
    """
    return previous + uptake + fixed


def fix_nitrogen(crop, soil) -> None:
    # TODO: this function needs updating once nitrogen_fixation.py is refactored
    crop.N_fix = calc_N_fixation(soil, crop)


def store_nitrogen_biomass(crop) -> None:
    """
    Description: updates the nitrogen biomass stored within a crop at the end of the day's growth cycle

    Args:
        crop: an instance of the BaseCrop class
    """
    crop.bio_N = calc_stored_nitrogen(uptake=crop.N_act_up, previous=crop.bio_N, fixed=crop.N_fix)
