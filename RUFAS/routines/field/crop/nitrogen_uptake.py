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
from itertools import accumulate
from RUFAS.routines.field.crop.nitrogen_fixation import calc_N_fixation

# TODO: These functions should probably be moved to the base_crop class as member functions


def update_all(crop_type, soil):
    """
    Description:
        Updates nitrogen uptake information for the given crop.

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
    """
    update_nitrogen_fraction(crop_type)
    update_optimal_nitrogen(crop_type)
    update_potential_nitrogen_uptake(crop_type)
    uptake_nitrogen(crop_type, soil)
    fix_nitrogen(crop_type)  # TODO: needs updating
    update_stored_nitrogen(crop_type)



def calc_nitrogen_fraction(phu_frac: float, nfrac_1: float, nfrac_3: float, shape1: float, shape2: float) -> float:
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

    # TODO: This used to be calculated from the **previous** day's values but I don't understand why. - Clay
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


def update_nitrogen_fraction(crop) -> None:
    """
    Description: update a crop's nitrogen fraction

    Args:
        crop: an instance of BaseCrop

    Returns: Nothing. Instead, the crop.fr_N attribute is updated.
    """
    shapes = calc_shape_parameters(heatfrac_half=crop.fr_PHU_50, heatfrac_full=crop.fr_PHU_100, nfrac_1=crop.fr_n1,
                                   nfrac_2=crop.fr_n2, nfrac_near=crop.fr_n3ish, nfrac_3=crop.fr_n3)
    # TODO: using current PHU and biomass instead of previous
    if crop.biomass_actual == 0:
        crop.fr_N = 0
    else:
        crop.fr_N = calc_nitrogen_fraction(phu_frac=crop.fr_PHU, nfrac_1=crop.fr_n1, nfrac_3=crop.fr_n3,
                                           shape1=shapes[0], shape2=shapes[1])


def calc_shape_parameters(heatfrac_half: float, heatfrac_full: float, nfrac_1: float, nfrac_2: float,
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


def calc_shape_log(heat_frac: float, nfrac_x: float, nfrac_3: float, nfrac_1: float) -> float:
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

    denominator = 1 - ((nfrac_x - nfrac_3) / (nfrac_1 - nfrac_3))

    if denominator > 1:  # leads to log(-y)
        raise ValueError("the quantity (nfrac_x-nfrac_3)/(nfrac_1-nfrac_3) is negative." +
                         "\nIs nfrac_x < nfrac_3 or nfrac_1 < nfrac_3?")
    # calculate results
    return log((heat_frac / denominator) - heat_frac)


def calc_optimal_nitrogen(nfrac: float, biomass: float) -> float:
    """
    Description:
        Calculates the optimal mass of nitrogen stored in plant biomass.
       "pseudocode_crop" C.5.B.2

    Args:
        nfrac: the fraction of the plant biomass that is nitrogen
        biomass: the biomass of the plant

    Returns:
        the optimal nitrogen mass
    """
    return nfrac * biomass


def update_optimal_nitrogen(crop) -> None:
    """
    Description:
        Updates a crops optimal nitrogen based on its current biomass and nitrogen fraction

    Args:
        crop: an instance of a BaseCrop object

    Returns:
        Nothing. Instead, crop.bio_N_opt is updated
    """
    crop.bio_N_opt += calc_optimal_nitrogen(nfrac=crop.fr_N, biomass=crop.biomass_actual)


def calc_potential_nitrogen_uptake(demand: float, nitrogen_start: float, mature_nfrac: float,
                                   max_growth: float) -> float:
    """
    Description:
        Calculates potential nitrogen uptake for a given day.
       "pseudocode_crop" C.5.B.3

    Args:
        demand: the nitrogen demand of a plant on a given day
        nitrogen_start: the actual biomass of nitrogen in the plant at the end of the previous day
        mature_nfrac:, the nitrogen fraction of the plant at maturity
        max_growth: the maximum potential biomass the plant can grow on a given day

    Returns:
        The potential nitrogen uptake for the day
    """
    return min(demand - nitrogen_start, 4 * mature_nfrac * max_growth)


def update_potential_nitrogen_uptake(crop) -> None:
    """
    Description:
        Update a plant's potential nitrogen uptake

    Args:
        crop: an instance of the BaseCrop class

    Returns:
        Nothing. Instead, updates crop.N_up
    """
    if crop.bio_N_opt - crop.prev_bio_N < 0:
        crop.N_up = 0
    else:
        # TODO: previous nitrogen biomass needs to be added to the crop class (.prev_bio_N)??
        #  This needs to be re-assessed in the context of the full routines (bio_N vs prev_bio_N)??
        crop.N_up = calc_potential_nitrogen_uptake(demand=crop.bio_N_opt, nitrogen_start=crop.prev_bio_N, mature_nfrac=crop.fr_n3,
                                                   max_growth=crop.d_biomass_max)


def calc_layer_nitrogen_uptake(layer_demand: list[float], layer_potential: list[float],
                               layer_nitrate: list[float]) -> list[float]:
    """
    Description:
        Calculates the actual nitrogen uptake from soil solution in each layer.
        Saves the list containing these values to act_N_up_each_layer attribute.
        The order of the values in the list corresponds with the order of the
        layers in soil.soil_layers. The soil layers in that list need to be in
        order of shallowest to deepest for this to work correctly.
        "pseudocode_crop" C.5.C.4/5/6/7

    Args:
        deficit: the demand for nitrogen by the plant not met by the above layers
        layer_nitrogen: a list of nitrogen amounts in each soil layer
        layer_nitrate: a list of nitrate amounts in each soil layer

    Returns:
        a list of the actual nitrogen taken up from each layer
    """

    if len(layer_potential) != len(layer_demand) or len(layer_potential) != len(layer_nitrate):
        raise ValueError("layer_potential, layer_demand, and layer_nitrate must be the same length")

    layer_desired = [potential + demand for potential, demand in zip(layer_potential, layer_demand)]
    return [min(desired, nitrate) for desired, nitrate in zip(layer_desired, layer_nitrate)]

def update_layer_nitrogen_uptake() -> None:
    # TODO: I'm not sure if this function is needed, or of uptake_nitrogen() should handle all updates
    #  I'm leaning toward the latter option.
    pass

def calc_layer_nitrogen_demand(uptake_potentials: list[float], nitrate_availabilities: list[float]) -> list[float]:
    """
    Description:
        calculates the nitrogen demand of the plant from each soil layer

    Args:
        uptake_potentials: the maximum potential nitrogen uptake by the plant from each soil layer
        nitrate_availabilities: the available nitrates (NO3) in each soil layer

    Returns: a list of nitrogen demands from each soil layer
    """
    layer_delta = [desired - available for desired, available in zip(uptake_potentials, nitrate_availabilities)]
    layer_demand = [sum(layer_delta[:i]) for i in range(len(layer_delta))] # cumulative sum
    return [max(val, 0) for val in layer_demand]  # constrain to zero

    # crop_type.pot_N_up_each_layer = calc_layer_nitrogen_potential(soil, crop_type)
    # act_N_up_each_layer = []
    #
    # # Running total of potential nitrogen uptake in overlying layers
    # N_up_over = 0
    #
    # # Running total of nitrate in overlying soil layers
    # NO3_over = 0
    #
    # # Nitrogen uptake demand not met in overlying soil layers
    # N_demand = 0
    #
    # for pot_N_up, soil_layer in zip(crop_type.pot_N_up_each_layer, soil.soil_layers):
    #
    #     # C.5.C.4
    #     act_N_up = min((pot_N_up + N_demand), soil_layer.NO3)
    #
    #     # C.5.C.7
    #     soil_layer.N_uptake = act_N_up
    #     act_N_up_each_layer.append(act_N_up)
    #
    #     # Update values so ready for the next layer
    #     N_up_over += pot_N_up
    #
    #     # C.5.C.6
    #     NO3_over += soil_layer.NO3
    #
    #     # C.5.C.5
    #     N_demand = max(N_up_over - NO3_over, 0)
    #
    #     if N_demand < 0:
    #         N_demand = 0
    #
    # crop_type.act_N_up_each_layer = act_N_up_each_layer

def uptake_nitrogen(crop, soil) -> None:
    """
    Description:
        uptake nitrogen from the soil and reallocate it into the crop

    Args:
        crop: an instance of the BaseCrop class
        soil: an instance of the Soil class
    """
    # pre-uptake conditions
    layer_bounds = [layer.bottom_depth for layer in soil.soil_layers]
    layer_nitrates = [layer.NO3 for layer in soil.soil_layers]
    # calculate layer values
    potentials = calc_layer_nitrogen_potential(boundaries=layer_bounds, demand=crop.N_up, root_depth=crop.z_root, ndistro=crop.beta_n)
    demands = calc_layer_nitrogen_demand(uptake_potentials=potentials, nitrate_availabilities=layer_nitrates)
    uptakes = calc_layer_nitrogen_uptake(layer_demand=demands, layer_potential=potentials, layer_nitrate=layer_nitrates)
    # update attributes
    for uptake, layer in zip(uptakes, soil.soil_layers):
        layer.N_uptake = uptake
        layer.NO3 -= uptake  # remove from soil
    crop.N_act_up = sum(uptakes)  # give to crop



def calc_layer_nitrogen_potential(boundaries: list[float], demand: float,
                                  root_depth: float, ndistro: float) -> list[float]:
    """
    Description:
        Calculates the potential nitrogen uptake from soil solution in each
        layer. Returns a list containing these values. The order of the values
        in the list corresponds with the order of the layers in
        soil.soil_layers. The soil layers in that list need to be in order of
        shallowest to deepest for this to work correctly.
       "pseudocode_crop" C.5.C.2/3

    Args:
        boundaries: a list of depths of the lower boundaries for each soil layer
        demand: the plants nitrogen demand
        root_depth: the current depth of the plant's roots
        ndistro: the nitrogen distribution parameter

    Returns:
        a list of potential nitrogen uptake from each layer
    """

    boundary_nitrogen = [calc_nitrogen_uptake_to_depth(demand, x, root_depth, ndistro) for x in boundaries]  # N at each boundary
    boundary_nitrogen.insert(0, 0)  # 0 N uptake at soil surface
    layer_nitrogen = [below - above for below, above in zip(boundary_nitrogen[1:], boundary_nitrogen)]  # subtract previous layer
    return layer_nitrogen


def calc_nitrogen_uptake_to_depth(demand: float, depth: float, root_depth: float, ndistro: float) -> float:
    """
    Description:
        Calculates potential nitrogen uptake from soil solution from the surface
        to a specified depth.
        "pseudocode_crop" C.5.C.1

    Args:
        demand: the current nitrogen demand
        depth: the depth to which nitrogen uptake is calculated
        root_depth: the current root depth
        ndistro: the nitrogen uptake distribution parameter

    Returns:
        the potential amount of nitrogen taken up
    """

    if ndistro == 0:
        raise ValueError("ndistro cannot equal 0")

    if root_depth <= 0:
        return 0
    else:
        first_term = demand / (1 - exp(-ndistro))
        second_term = 1 - exp(-ndistro * (depth / root_depth))
        return first_term * second_term


def calc_stored_nitrogen(uptake: float, previous: float, fixed: float = 0) -> float:
    """
    Description:
        Calculates actual mass of nitrogen stored in plant material on the current day.
        "pseudocode_crop" C.5.E.1

    Args:
        uptake: the mass of the nitrogen taken up by the plant on the current day
        previous: the mass of the plant's stored nitrogen from the previous day
        fixed: the mass of nitrogen fixed by the plant on the current day

    Returns:
        the total mass of nitrogen in the plant on the current day
    """
    return previous + uptake + fixed
    # crop_type.N_fix = calc_N_fixation(soil, crop_type)
    # crop_type.bio_N = crop_type.bio_N + crop_type.N_act_up + crop_type.N_fix


def fix_nitrogen(crop, soil) -> None:
    crop.N_fix = calc_N_fixation(soil, crop)

def update_stored_nitrogen(crop) -> None:
    """
    Description: updates the nitrogen biomass of a crop

    Args:
        crop: an instance of the BaseCrop class
    """
    crop.bio_N = calc_stored_nitrogen(uptake=crop.N_act_up, previous=crop.bio_N, fixed=crop.N_fix)
