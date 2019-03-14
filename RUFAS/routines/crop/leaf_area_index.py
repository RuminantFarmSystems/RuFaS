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

    l1 = shape coefficient

    l2 = shape coefficient

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
    l1, l2 = calculate_shape_coefficients(crop_type)
    calc_fr_LAI_max(crop_type, time, l1, l2)
    calculate_LAI_actual(crop_type, time)


#
# Calculate shape coefficients for LAI accumulation.
# "pseudocode_SC_cropbiomass.docx" section 1.D.1
#
def calculate_shape_coefficients(crop_type):
    l2_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1
    l2_part2 = (crop_type.fr_PHU_2 / crop_type.fr_LAI_2) - crop_type.fr_PHU_2

    l2 = ((log(l2_part1) - log(l2_part2))
          / (crop_type.fr_PHU_2 - crop_type.fr_PHU_1))

    l1_part1 = (crop_type.fr_PHU_1 / crop_type.fr_LAI_1) - crop_type.fr_PHU_1

    l1 = log(l1_part1) + l2 * crop_type.fr_PHU_1

    return l1, l2


#
# This function calculates the accumulated fraction of LAI maximum accumulated
# including today.
# "pseudocode_SC_cropbiomass.docx" section 1.D.2
#
def calc_fr_LAI_max(crop_type, time, l1, l2):
    crop_type.prev_fr_LAI_max = crop_type.fr_LAI_max

    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date

    if not inGrowingPeriod:
        crop_type.fr_LAI_max = 0
    else:
        exp_part = exp(l1 - l2 * crop_type.fr_PHU)
        crop_type.fr_LAI_max = crop_type.fr_PHU / (crop_type.fr_PHU + exp_part)


#
# This function calculates LAI_actual. The equations for calculating dLAI_max
# and LAI_actual can be found in "pseudocode_SC_cropbiomass.docx" in
# section 1.D.3 and 1.D.4 respectively.
#
def calculate_LAI_actual(crop_type, time):
    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date
    crop_type.prev_LAI_actual = crop_type.LAI_actual

    if not inGrowingPeriod:
        dLAI_max = 0
        dLAI_actual = 0

    elif crop_type.fr_PHU < crop_type.fr_PHU_sen:
        # 1.D.3
        exp_part = exp(5 * (crop_type.prev_LAI_actual - crop_type.LAI_max))
        d_fr_LAI_max = (crop_type.fr_LAI_max - crop_type.prev_fr_LAI_max)
        dLAI_max = d_fr_LAI_max * crop_type.LAI_max * (1 - exp_part)
        dLAI_actual = calculate_dLAI_actual(crop_type, dLAI_max)

        # 1.D.4.a.1
        crop_type.LAI_actual = crop_type.prev_LAI_actual + dLAI_actual

    else:

        # 1.D.4.a.2
        LAI_actual = crop_type.LAI_max * (1 - crop_type.fr_PHU) / (1 - crop_type.fr_PHU_sen)
        crop_type.LAI_actual = max(LAI_actual, 0)

        # 1.D.4.a.1 (LAIi = LAIi-1 + dLAIi, dLAI = LAIi - LAIi-1)
        dLAI_max = crop_type.LAI_actual - crop_type.prev_LAI_actual
        dLAI_actual = calculate_dLAI_actual(crop_type, dLAI_max)

    # Return these calculated values just so they can be used in testing/debugging
    return dLAI_max, dLAI_actual


#
# This function calculates dLAI_actual for use in calculating dLAI_max and LAI_actual
# on a given day. The equations for calculating dLAI_actual can be found in
# "pseudocode_SC_actualgrowth.docx" in section 7.A.3
#
def calculate_dLAI_actual(crop_type, dLAI_max):
    return dLAI_max * sqrt(crop_type.gamma_reg)
