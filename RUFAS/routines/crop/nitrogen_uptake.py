'''
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_uptake.py

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
    n2 = calc_n2(crop_type)
    n1 = calc_n1(crop_type, n2)
    calc_fr_N(crop_type, n1, n2)
    calc_bio_N_opt(crop_type)
    calc_N_up(crop_type)
    record_results(crop_type, time)


def calc_n2(crop_type):
    term1 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2
    )

    term2 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_100, crop_type.fr_n3ish
    )

    term3 = crop_type.fr_PHU_100 - crop_type.fr_PHU_50

    return (term1 - term2) / term3


def calc_n1(crop_type, n2):
    term1 = calc_log_term_of_shape_coeff(
        crop_type, crop_type.fr_PHU_50, crop_type.fr_n2
    )

    return term1 + n2 * crop_type.fr_PHU_50


def calc_log_term_of_shape_coeff(crop_type, fr_PHU_fract, fr_n_):
    bottom = 1 - (fr_n_ - crop_type.fr_n3) / (crop_type.fr_n1 - crop_type.fr_n3)
    inside = (fr_PHU_fract / bottom) - fr_PHU_fract
    return log(inside)


def calc_fr_N(crop_type, n1, n2):
    if crop_type.prev_biomass_actual == 0:
        crop_type.fr_N = 0
    else:
        term1 = crop_type.fr_n1

        exp_part = exp(n1 - n2 * crop_type.prev_fr_PHU)
        term2 = 1 - crop_type.prev_fr_PHU / (crop_type.prev_fr_PHU + exp_part)

        crop_type.fr_N = term1 * term2 + crop_type.fr_n3


def calc_bio_N_opt(crop_type):
    crop_type.bio_N_opt = crop_type.fr_N * crop_type.prev_biomass_actual


def calc_N_up(crop_type):
    if crop_type.bio_N_opt - crop_type.bio_N < 0:
        crop_type.N_up = 0
    else:
        option1 = crop_type.bio_N_opt - crop_type.bio_N
        option2 = 4 * crop_type.fr_n3 * crop_type.dBiomass_max
        crop_type.N_up = 1.5 * min(option1, option2)


#==============================================================================

''' The following can be used for testing purposes '''

#
# The file that will record results of the root depth calculations.
# This is for testing purposes.
#
test_file = "tests/crop_test_files/nitrogen_uptake_results.csv"

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
            crop_type.fr_N,
            crop_type.bio_N_opt,
            crop_type.N_up
        )
        if time.day == 1 and time.year == 1:
            resultFile.write("day,prev_biomass_actual,fr_N,bio_N_opt,N_up\n")
        resultFile.write(result)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass