"""
RUFAS: Ruminant Farm Systems Model

File name: yields.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the yield values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    HI_min = Harvest index for the plants in drought conditions

    HI_max = Max potential harvest index for a given day

    gamma_wu = Water deficiency factor

    ET_sum = Sum of actual evapotranspiration from day 1 up to today (mm H20)

    Eo_sum = Sum of potential evapotranspiration from day 1 up to today (mm H20)

    HI_actual = Actual harvest index

    HI_opt = Potential harvest for the plant at maturity given ideal growing
             conditions

    bio_AG = Aboveground biomass (kg ha^-1)

    harvest_eff = Efficiency of the harvest operation, i.e. fraction of yield
                  biomass removed by the harvesting equipment.

    yield_max = maximum crop yield at harvest (kg ha^-1)

    yield_actual = Actual crop yield at harvest (kg ha^-1)

    yield_N = Amount of nitrogen removed in the yield

    yield_P = Amount of phosphorus removed in the yield

    residue = Material in the residue pool for the top 10mm of soil on current
              day (kg ha^-1)


CropType values updated by update_all():

    gamma_wu
    HI_max
    bio_AG
    HI_actual
    yield_max
    yield_actual
    yield_N
    yield_P
    residue
"""
###############################################################################
from math import exp


#
# Runs all the yield calculations
#
def update_all(crop_type, time, soil):
    calc_gamma_wu(crop_type, soil)
    calc_HI_max(crop_type)
    calc_bio_AG(crop_type)
    calc_HI_actual(crop_type, time)
    calc_yield_max(crop_type, time)
    calc_yield_act(crop_type)
    calc_nutrient_removal(crop_type)
    calc_residue(crop_type, time, soil)


#
# Calculates water deficiency factor (AKA gamma_wu).
# "pseudocode_crop" C.10.A.1
#
def calc_gamma_wu(crop_type, soil):
    if soil.ET_max_annual == 0:
        return 0
    crop_type.ET_annual = soil.evap_annual + soil.trans_annual
    crop_type.gamma_wu = 100 * (crop_type.ET_annual / soil.ET_max_annual)


#
# Calculates max potential harvest index for a given day.
# "pseudocode_crop" C.10.B.1
#
def calc_HI_max(crop_type):
    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - (10 * crop_type.fr_PHU))
    crop_type.HI_max = crop_type.HI_opt * top / bottom


#
# Calculates aboveground biomass.
# "pseudocode_crop" C.10.C.1
#
def calc_bio_AG(crop_type):
    crop_type.bio_AG = (1 - crop_type.fr_root) * crop_type.biomass_actual


#
# Calculates the actual harvest index (AKA HI_actual).
# "pseudocode_crop" C.10.D.1
#
def calc_HI_actual(crop_type, time):
    in_growing_period = crop_type.start_date <= time.day <= crop_type.harvest_date
    # if time.day >= crop_type.start_date:
    term1 = crop_type.HI_max - crop_type.HI_min
    exp_part = exp(6.13 - (0.883 * crop_type.gamma_wu))
    term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)

    crop_type.HI_actual = term1 * term2 + crop_type.HI_min


#
# Calculates maximum crop yield at harvest.
# "pseudocode_crop" C.10.E.1
#
def calc_yield_max(crop_type, time):
    if time.day == crop_type.harvest_date:
        crop_type.yield_max = crop_type.bio_AG * crop_type.HI_max
    else:
        crop_type.yield_max = 0


#
# Calculates actual crop yield at harvest.
# "pseudocode_crop" C.10.F.1
#
def calc_yield_act(crop_type):
    crop_type.yield_actual = crop_type.yield_max * crop_type.harvest_eff


#
# Calculates the amount of nitrogen and phosphorus removed in the yield.
# "pseudocode_crop" C.10.G.1/2
#
def calc_nutrient_removal(crop_type):
    crop_type.yield_N = crop_type.fr_N * crop_type.yield_actual
    crop_type.yield_P = crop_type.fr_P * crop_type.yield_actual


#
# Updates the current residue.
# # "pseudocode_crop" C.10.H.1/2
#
def calc_residue(crop_type, time, soil):
    dResidue = 0
    if crop_type.harvest_date == time.day:
        # This is where we differentiate between a kill and a harvest.
        # The primary difference being that root biomass is added to residue.
        # This also replaces the annual update, adjusting biomass @ harvest
        if crop_type.kill_year:
            dResidue = crop_type.biomass_actual - crop_type.yield_actual
            kill(crop_type)
        else:
            bio_frac = crop_type.yield_actual / crop_type.bio_AG
            harvest(crop_type, bio_frac)
    soil.residue += dResidue


def kill(crop_type):
    crop_type.accumulated_HU = 0
    crop_type.prev_accumulated_HU = 0

    crop_type.fr_PHU = 0
    crop_type.prev_fr_PHU = 0

    crop_type.fr_LAI_max = 0

    crop_type.biomass_actual = 0
    crop_type.prev_biomass_actual = 0
    crop_type.bio_AG = 0

    crop_type.z_root = 0
    crop_type.fr_root = 0

    crop_type.bio_P = 0
    crop_type.bio_N = 0

    crop_type.HI_actual = 0

    crop_type.ET_annual = 0

    crop_type.planted = False


def harvest(crop_type, bio_frac):
    crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)

    crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)

    crop_type.biomass_actual -= crop_type.yield_actual
    crop_type.bio_AG -= crop_type.yield_actual

    crop_type.bio_P = 0
    crop_type.bio_N = 0

    crop_type.ET_annual = 0
