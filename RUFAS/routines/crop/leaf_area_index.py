'''
RUFAS: Ruminant Farm Systems Model

File name: heat_units.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the Leaf Area Index of the current day. The only function
             that is meant to be called outside of this module is update_all()

Variable definitions:

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
    results = calculate_LAI_actual(crop_type, time)
    record_results(crop_type, time, results)


#
# Calculate shape coefficients for LAI accumulation. The equations for these
# calculations can be found in "Pseudo code_SC_maxdeltabio_1.0.docx" in
# section 1.D.1
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
# including today. This can be found in "Pseudo code_SC_maxdeltabio_1.0.docx"
# in section 1.D.2
#
def calc_fr_LAI_max(crop_type, time, l1, l2):
    crop_type.prev_fr_LAI_max = crop_type.fr_LAI_max

    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date
    if not inGrowingPeriod:
        crop_type.fr_LAI_max = 0
    else:
        crop_type.fr_LAI_max = crop_type.fr_PHU / (crop_type.fr_PHU + exp(l1 - l2 * crop_type.fr_PHU))


#
# This function calculates LAI_actual. The equations for calculating dLAI_max
# and LAI_actual can be found in "Pseudo code_SC_maxdeltabio_1.0.docx" in
# section 1.D.3 and 1.D.4 respectively. The equations for calculating
# dLAI_actual can be found in "Pseudo code_SC_actual growth and yield_1.0.docx"
# in section 7.A.3
#
def calculate_LAI_actual(crop_type, time):
    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date
    crop_type.prev_LAI_actual = crop_type.LAI_actual

    if not inGrowingPeriod:
        dLAI_max = 0
        dLAI_actual = 0

    elif crop_type.fr_PHU < crop_type.fr_PHU_sen:
        #print("%i, %f" % (time.day, crop.prev_LAI_actual))
        exp_part = exp(5 * (crop_type.prev_LAI_actual - crop_type.LAI_max))
        dLAI_max = (crop_type.fr_LAI_max - crop_type.prev_fr_LAI_max) * crop_type.LAI_max * (1 - exp_part)
        dLAI_actual = dLAI_max * sqrt(crop_type.gamma_reg)
        crop_type.LAI_actual = crop_type.prev_LAI_actual + dLAI_actual

    else:
        result = crop_type.LAI_max * (1 - crop_type.fr_PHU) / (1 - crop_type.fr_PHU_sen)
        crop_type.LAI_actual = max(result, 0)
        dLAI_max = crop_type.LAI_actual - crop_type.prev_LAI_actual
        dLAI_actual = dLAI_max * sqrt(crop_type.gamma_reg)

    return (dLAI_max, dLAI_actual)

# ==============================================================================

''' The following can be used for testing purposes '''

#
# The file that will record results of the leaf area index calculations.
# This is for testing purposes.
#
lai_test_file = "tests/crop_test_files/LAI_results.csv"

#
# The following will record the leaf area index calculations into the test
# file.
#
def record_results(crop_type, time, results):
    if time.day == 1 and time.year == 1:
        reset_file(lai_test_file)

    with open(lai_test_file, "a") as resultFile:
        dLAI_max = results[0]
        dLAI_actual = results[1]
        info = "%i,%f,%f,%f,%f,%f,%f\n" %\
                 (time.day, crop_type.fr_PHU, crop_type.fr_LAI_max, dLAI_max, crop_type.gamma_reg, dLAI_actual, crop_type.LAI_actual)

        if time.day == 1 and time.year == 1:
            resultFile.write("time.day,fr_PHU,fr_LAI_max,dLAI_max,gamma_reg,dLAI_actual,LAI_actual\n")
        resultFile.write(info)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass