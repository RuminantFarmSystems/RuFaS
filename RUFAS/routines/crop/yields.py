'''
RUFAS: Ruminant Farm Systems Model

File name: heat_units.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description:

Variable definitions:

'''
###############################################################################
from math import exp

#
# Runs all the yield calculations
#
def update_all(crop_type, time):
    calc_gamma_wu(crop_type)
    calc_HI_max(crop_type)
    calc_bio_AG(crop_type)
    calc_HI_actual(crop_type, time)
    calc_yield_max(crop_type, time)
    calc_yield_actual(crop_type)
    record_results(crop_type, time)


#
# Calculates water deficiency factor (AKA gamma_wu) according to
# "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.B.1
#
def calc_gamma_wu(crop_type):
    crop_type.gamma_wu = 100*(crop_type.Ea_sum/crop_type.Eo_sum)


#
# Calculates the actual harvest index (AKA HI_actual) according to
# "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.B.2
#
def calc_HI_actual(crop_type, time):
    inGrowingPeriod = crop_type.planting_date <= time.day <= crop_type.harvest_date
    if not inGrowingPeriod:
        crop_type.HI_actual = 0
    else:
        term1 = crop_type.HI_max - crop_type.HI_min

        exp_part = exp(6.13 - 0.883*crop_type.gamma_wu)
        term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)

        crop_type.HI_actual = term1 * term2 + crop_type.HI_min


#
#
#
def calc_HI_max(crop_type):
    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - 10*crop_type.fr_PHU)
    crop_type.HI_max = crop_type.HI_opt * top / bottom


#
#
#
def calc_bio_AG(crop_type):
    crop_type.bio_AG = (1-crop_type.fr_root) * crop_type.biomass_actual


#
#
#
def calc_yield_max(crop_type, time):
    if time.day == crop_type.harvest_date:
        crop_type.yield_max =  crop_type.bio_AG * crop_type.HI_actual
    else:
        crop_type.yield_max = 0


#
# Found in "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.B.3
#
def calc_yield_actual(crop_type):
    crop_type.yield_actual = crop_type.harvest_eff * crop_type.yield_max


#==============================================================================

''' The following is for testing purposes '''

#
# The file that will record results of the yield calculations.
#
yield_test_file = "tests/crop_test_files/yield_results.csv"

#
# The following will record the root depth calculations into the
# test file.
#
def record_results(crop_type, time):
    if time.day == 1 and time.year == 1:
        reset_file(yield_test_file)
    with open(yield_test_file, "a") as resultFile:
        result = "%i,%f,%f,%f,%f,%f\n" % (
            time.day,
            crop_type.gamma_wu,
            crop_type.bio_AG,
            crop_type.HI_actual,
            crop_type.yield_max,
            crop_type.yield_actual
        )
        if time.day == 1 and time.year == 1:
            resultFile.write("day,gamma wu,bioAG,HI_actual,yield_max,yield_actual\n")

        if time.day == crop_type.harvest_date:
            resultFile.write(result)


def reset_file(fileName):
    with open(fileName, "w") as file:
        pass