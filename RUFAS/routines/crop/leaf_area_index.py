'''
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

    dLAI_max = Maximum leaf area added on current day

    dLAI_actual = Actual leaf area added on current day


CropType values updated by update_all():

    prev_fr_LAI_max
    fr_LAI_max
    LAI_actual
    prev_LAI_actual
'''
###############################################################################

from math import exp, log, sqrt


#
# This function calls all the necessary functions to update information related
# to the leaf area index.
#
def update_all(crop_type, time):
    L1, L2 = calculate_shape_coefficients(crop_type)
    calc_fr_LAI_max(crop_type, time, L1, L2)
    calculate_LAI_actual(crop_type, time)


#
# Calculate shape coefficients for LAI accumulation.
# "pseudocode_crop" section 8.A.1/2
#
def calculate_shape_coefficients(crop_type):
    # 8.A.1
    L2_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1
    L2_part2 = (crop_type.fr_PHU_2 / crop_type.fr_LAI_2) - crop_type.fr_PHU_2

    L2 = ((log(L2_part1) - log(L2_part2))
          / (crop_type.fr_PHU_2 - crop_type.fr_PHU_1))

    # 8.A.2
    L1_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1

    L1 = log(L1_part1) + (L2 * crop_type.fr_PHU_1)

    return L1, L2


#
# This function calculates the accumulated fraction of LAI maximum accumulated
# including today.
# "pseudocode_crop" section 8.A.3
#
def calc_fr_LAI_max(crop_type, time, L1, L2):
    crop_type.prev_fr_LAI_max = crop_type.fr_LAI_max

    growing_period = crop_type.start_date <= time.day <= crop_type.harvest_date

    if not growing_period:
        crop_type.fr_LAI_max = 0
    else:
        exp_part = exp(L1 - (L2 * crop_type.fr_PHU))
        crop_type.fr_LAI_max = crop_type.fr_PHU / (crop_type.fr_PHU + exp_part)


#
# This function calculates LAI_actual.
# "pseudocode_crop" section 8.A.4/6
#
def calculate_LAI_actual(crop_type, time):
    growing_period = crop_type.start_date <= time.day <= crop_type.harvest_date
    prev_LAI_actual = crop_type.LAI_actual

    if growing_period:

        # 8.A.4
        exp_part = exp(5 * (prev_LAI_actual - crop_type.LAI_max))
        d_fr_LAI_max = (crop_type.fr_LAI_max - crop_type.prev_fr_LAI_max)
        dLAI_max = d_fr_LAI_max * crop_type.LAI_max * (1 - exp_part)
        dLAI_actual = calculate_dLAI_actual(crop_type, dLAI_max)

        if crop_type.fr_PHU < crop_type.fr_PHU_sen:
            # 8.A.6
            crop_type.LAI_actual = prev_LAI_actual + dLAI_actual

        else:
            # 8.A.6
            LAI_actual = crop_type.LAI_max * (1 - crop_type.fr_PHU) / (1 - crop_type.fr_PHU_sen)
            crop_type.LAI_actual = max(LAI_actual, 0)


#
# This function calculates dLAI_actual for use in calculating dLAI_max and LAI_actual
# on a given day. The equations for calculating dLAI_actual can be found in
# "pseudocode_crop" section8.A.5
#
def calculate_dLAI_actual(crop_type, dLAI):
    return dLAI * sqrt(crop_type.gamma_reg)

