from math import exp, log, sqrt

"""
This module is based off of the 'Canopy Cover and Height' section of SWAT
"""







def calc_optimal_leaf_area_fraction(heat_fraction: float, shape1: float, shape2: float) -> float:
    """calculates leaf area index fraction, from the optimal leaf area development curve, for the initial period of
    plant growth

    Args:
        heat_fraction: fraction of potential heat units
        shape1: first shape coefficient
        shape2: second shape coefficient

    Returns:
        fraction of the plant's maximum leaf area index
    """
    return heat_fraction / (heat_fraction + exp(shape1 - (shape2 * heat_fraction)))


def calc_shape_log(heat_fraction: float, leaf_area_fraction: float) -> float:
    """calculates the log term of LAI shape parameter function"""
    return log(heat_fraction/leaf_area_fraction - heat_fraction)

def calc_shape_parameters(first_heat_fraction: float, second_heat_fraction: float,
                          first_leaf_fraction: float, second_leaf_fraction: float) -> list[float]:
    """calculates the shape coefficients for """

    first_log = calc_shape_log(first_heat_fraction, first_leaf_fraction)
    second_log = calc_shape_log(second_heat_fraction, second_leaf_fraction)

    second_shape = (first_log - second_log) / (first_heat_fraction - second_heat_fraction)
    first_shape = first_log + (second_shape * first_heat_fraction)

    return [first_shape, second_shape]



def update_all(crop_type):
    """
    Description:
        Calls all the necessary functions to update information
        related to the leaf area index for the given crop_type.

    Args:
        crop_type: an instance of a crop
    """
    L1, L2 = calculate_shape_coefficients(crop_type)
    calc_fr_LAI_max(crop_type, L1, L2)
    calculate_LAI_actual(crop_type)


def calculate_shape_coefficients(crop_type):
    """
    Description:
        Calculate shape coefficients for LAI accumulation.
        "pseudocode_crop" section C.8.A.1/2

    Args:
        crop_type
    Returns:
        int: shape coefficients
    """
    # 8.A.1
    L2_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1
    L2_part2 = (crop_type.fr_PHU_2 / crop_type.fr_LAI_2) - crop_type.fr_PHU_2

    L2 = ((log(L2_part1) - log(L2_part2))
          / (crop_type.fr_PHU_2 - crop_type.fr_PHU_1))

    # C.8.A.2
    L1_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1

    L1 = log(L1_part1) + (L2 * crop_type.fr_PHU_1)

    return L1, L2



def calc_fr_LAI_max(crop_type, L1, L2):
    """
    Description:
        Calculates the accumulated fraction of LAI maximum
        accumulated including today for the given crop type.
        "pseudocode_crop" section C.8.A.3

    Args:
        crop_type
        L1: first shape coefficient
        L2: second shape coefficient
    """

    crop_type.prev_fr_LAI_max = crop_type.fr_LAI_max

    exp_part = exp(L1 - (L2 * crop_type.fr_PHU))
    crop_type.fr_LAI_max = crop_type.fr_PHU / (crop_type.fr_PHU + exp_part)


def calculate_LAI_actual(crop_type):
    """
    Description:
        This calculates LAI_actual for the given crop_type.
        "pseudocode_crop" section C.8.A.4/6

    Args:
        crop_type
    """

    # C.8.A.4
    exp_part = exp(5 * (crop_type.LAI_actual - crop_type.LAI_max))
    d_fr_LAI_max = (crop_type.fr_LAI_max - crop_type.prev_fr_LAI_max)
    d_LAI_max = d_fr_LAI_max * crop_type.LAI_max * (1 - exp_part)
    d_LAI_actual = calculate_d_LAI_actual(crop_type, d_LAI_max)

    if crop_type.fr_PHU <= crop_type.fr_PHU_sen:
        # C.8.A.6
        crop_type.LAI_actual = crop_type.LAI_actual + d_LAI_actual
        crop_type.LAI_actual = max(crop_type.LAI_actual, 0)
    else:
        # C.8.A.6
        crop_type.LAI_actual = crop_type.LAI_actual * (1 - crop_type.fr_PHU) / (1 - crop_type.fr_PHU_sen)
        crop_type.LAI_actual = max(crop_type.LAI_actual, 0)


def calculate_d_LAI_actual(crop_type, d_LAI_max):
    """
    Description:
        Calculates d_LAI_actual for use in calculating d_LAI_max and
        LAI_actual on a given day for the given crop.
        "pseudocode_crop" C.8.A.5

    Args:
        crop_type
        d_LAI_max: change in LAI maximum
    Returns:
        float: change in LAI actual
    """

    return d_LAI_max * sqrt(crop_type.gamma_reg)
