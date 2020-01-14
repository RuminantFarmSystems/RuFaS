"""
RUFAS: Ruminant Farm Systems Model

File name: leaf_area_index.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the Leaf Area Index of the current day. The only function
             that is meant to be called outside of this module is update_all()

CropType attribute definitions:

    fr_PHU_1 = crop-specific curve point

    fr_PHU_2 = crop-specific curve point

    fr_LAI_1 = crop-specific curve point

    fr_LAI_2 = crop-specific curve point

    L1 = shape coefficient

    L2 = shape coefficient

    fr_PHU = Fraction of PHU accumulated by current day

    fr_LAI_max = fraction of the plant's maximum leaf area index corresponding
                 to a given fraction of potential heat units for the plant

    prev_fr_LAI_max = fr_LAI_max leading up to the current day

    LAI_max = Crop-specific maximum LAI

    d_LAI_max = Maximum leaf area added on current day

    d_LAI_actual = Actual leaf area added on current day


CropType values updated by update_all():

    prev_fr_LAI_max
    fr_LAI_max
    LAI_actual
    prev_LAI_actual
"""

from math import exp, log, sqrt


def update_all(crop_type):
    """This function calls all the necessary functions to update information
        related to the leaf area index.

    Inputs:
        crop_type
    """
    L1, L2 = calculate_shape_coefficients(crop_type)
    calc_fr_LAI_max(crop_type, L1, L2)
    calculate_LAI_actual(crop_type)


def calculate_shape_coefficients(crop_type):
    """Calculate shape coefficients for LAI accumulation.
       "pseudocode_crop" section C.8.A.1/2

    Inputs:
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
    """This function calculates the accumulated fraction of LAI maximum
       accumulated including today.
       "pseudocode_crop" section C.8.A.3

    Inputs:
        crop_type
        L1
        L2
    """

    crop_type.prev_fr_LAI_max = crop_type.fr_LAI_max

    exp_part = exp(L1 - (L2 * crop_type.fr_PHU))
    crop_type.fr_LAI_max = crop_type.fr_PHU / (crop_type.fr_PHU + exp_part)


def calculate_LAI_actual(crop_type):
    """This function calculates LAI_actual.
       "pseudocode_crop" section C.8.A.4/6

    Inputs:
        crop_type
    """

    prev_LAI_actual = crop_type.LAI_actual

    # C.8.A.4
    exp_part = exp(5 * (prev_LAI_actual - crop_type.LAI_max))
    d_fr_LAI_max = (crop_type.fr_LAI_max - crop_type.prev_fr_LAI_max)
    d_LAI_max = d_fr_LAI_max * crop_type.LAI_max * (1 - exp_part)
    d_LAI_actual = calculate_d_LAI_actual(crop_type, d_LAI_max)

    if crop_type.fr_PHU < crop_type.fr_PHU_sen:
        # C.8.A.6
        crop_type.LAI_actual = prev_LAI_actual + d_LAI_actual
        crop_type.LAI_actual = max(crop_type.LAI_actual, 0)
    else:
        # C.8.A.6
        # TODO: previous equation (and SWAT) use LAI_max as the multiplier
        #  instead of LAI_actual but it caused massive spikes near senescence
        crop_type.LAI_actual = crop_type.LAI_actual * (1 - crop_type.fr_PHU) / (1 - crop_type.fr_PHU_sen)
        crop_type.LAI_actual = max(crop_type.LAI_actual, 0)


def calculate_d_LAI_actual(crop_type, d_LAI_max):
    """This function calculates d_LAI_actual for use in calculating d_LAI_max and
       LAI_actual on a given day.
       "pseudocode_crop" C.8.A.5

    Inputs:
        crop_type
        d_LAI_max: change in LAI maximum
    Returns:
        float: change in LAI actual
    """
    return d_LAI_max * sqrt(crop_type.gamma_reg)
