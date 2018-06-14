'''
RUFAS: Ruminant Farm Systems Model

File name: yields.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the yield values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

Variable definitions:

    HI_min = Harvest index for the plants in drought conditions

    HI_max = Max potential harvest index for a given day

    gamma_wu = Water deficiency factor

    Ea_sum = Sum of actual evapotranspiration from day 1 up to today (mm H20)

    Eo_sum = Sum of potential evapotranspiration from day 1 up to today (mm H20)

    HI_actual = Actual harvest index

    HI_opt = Potential harvest for the plant at maturity given ideal growing
             conditions

    bio_AG = Aboveground biomass (kg ha^-1)

    harvest_eff = Efficiency of the harvest operation, i.e. fraction of yield
                  biomass removed by the harvesting equipment.

    yield_max = maximum crop yield at harvest (kg ha^-1)

    yield_actual = Actual crop yield at harvest (kg ha^-1)


CropType values updated by update_all():
    gamma_wu
    HI_max
    bio_AG
    HI_actual
    yield_max
    yield_actual

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
# Calculates water deficiency factor (AKA gamma_wu).
# "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.B.1
#
def calc_gamma_wu(crop_type):
    crop_type.gamma_wu = 100*(crop_type.Ea_sum/crop_type.Eo_sum)


#
# Calculates max potential harvest index for a given day.
# "Pseudo code_SC_crop yield_1.1.docx" section 5.1
#
def calc_HI_max(crop_type):
    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - 10*crop_type.fr_PHU)
    crop_type.HI_max = crop_type.HI_opt * top / bottom


#
# Calculates aboveground biomass.
# "Pseudo code_SC_crop yield_1.1.docx" section 5.2
#
def calc_bio_AG(crop_type):
    crop_type.bio_AG = (1-crop_type.fr_root) * crop_type.biomass_actual


#
# Calculates the actual harvest index (AKA HI_actual).
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
# Calculates maximum crop yield at harvest.
# "Pseudo code_SC_crop yield_1.1.docx" section 5.3
#
def calc_yield_max(crop_type, time):
    if time.day == crop_type.harvest_date:
        crop_type.yield_max =  crop_type.bio_AG * crop_type.HI_actual
    else:
        crop_type.yield_max = 0


#
# Calculates actual crop yield at harvest.
# "Pseudo code_SC_actual growth and yield_1.0.docx" section 7.B.3
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