'''
RUFAS: Ruminant Farm Systems Model

File name: phosphorus_uptake.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description:

Variable definitions:


CropType values updated by calling update_all():

'''
###############################################################################

from math import log, exp

#
#
#
def update_all(crop_type, time):
    p2 = calc_p2(crop_type)
    p1 = calc_p1(crop_type, p2)
    calc_fr_P(crop_type, p1, p2)
    calc_bio_P_opt(crop_type)
    calc_P_up(crop_type)
    record_results(crop_type, time)

def calc_p2(crop_type):
    first_term = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    second_term = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_100, crop_type.fr_p3ish
    )

    third_term = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (first_term - second_term) / third_term


def calc_p1(crop_type, p2):
    first_term = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_p2
    )

    return first_term + p2 * crop_type.fr_PHU_50


def calc_log_term_of_shape_coeff(crop_type, fr_PHU_fract, fr_p_):
    bottom = 1 - (fr_p_ - crop_type.fr_p3) / (crop_type.fr_p1 - crop_type.fr_p3)
    inside = (fr_PHU_fract / bottom) - fr_PHU_fract
    return log(inside)


def calc_fr_P(crop_type, p1, p2):
    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_P = 0
    else:
        first_term = crop_type.fr_p1 - crop_type.fr_p3

        exp_part = exp(p1 - p2 * crop_type.prev_fr_PHU)
        second_term = 1 - (crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part))

        crop_type.fr_P = first_term * second_term + crop_type.fr_p3


def calc_bio_P_opt(crop_type):
    crop_type.bio_P_opt = crop_type.prev_biomass_actual * crop_type.fr_P


def calc_P_up(crop_type):
    if crop_type.bio_P_opt - crop_type.bio_P < 0:
        crop_type.P_up = 0
    else:
        option1 = crop_type.bio_P_opt - crop_type.bio_P
        option2 = 4 * crop_type.fr_p3 * crop_type.dBiomass_max
        crop_type.P_up = 1.5 * min(option1, option2)



#==============================================================================

''' The following can be used for testing purposes '''

#
# The file that will record results of the root depth calculations.
# This is for testing purposes.
#
test_file = "tests/crop_test_files/phosphorus_uptake_results.csv"

#
# The following will record the root depth calculations into the
# test file.
#
def record_results(crop_type, time):
    if time.day == 1 and time.year == 1:
        reset_file((test_file))

    with open(test_file, "a") as resultFile:
        result = "%i,%f,%f,%f,%f\n" % (
            time.day,
            crop_type.prev_biomass_actual,
            crop_type.fr_P,
            crop_type.bio_P_opt,
            crop_type.P_up
        )
        if time.day == 1 and time.year == 1:
            resultFile.write("day,prev_biomass_actual,fr_P,bio_P_opt,P_up\n")
        resultFile.write(result)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass