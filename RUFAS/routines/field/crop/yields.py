"""
RUFAS: Ruminant Farm Systems Model

File name: yields.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu
           William Donovan, wmdonovan@wisc.edu
           Jacob Johnson, jacob8399@gmail.com

Description: This module contains the necessary functions for calculating and
             updating the yield values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    HI_min = Harvest index for the plants in drought conditions

    HI_max = Max potential harvest index for a given day

    gamma_wu = Water deficiency factor

    ET_annual = Sum of actual evapotranspiration from day 1 up to today (mm H20)

    ET_max_annual = Sum of potential evapotranspiration from day 1 up to today (mm H20)

    HI_actual = Actual harvest index

    HI_opt = Potential harvest for the plant at maturity given ideal growing
             conditions

    bio_AG = Aboveground biomass (kg/ha)

    harvest_eff = Efficiency of the harvest operation, i.e. fraction of yield
                  biomass removed by the harvesting equipment.

    yield_max = maximum crop yield at harvest (kg/ha)

    yield_actual = Actual crop yield at harvest (kg/ha)

    yield_N = Amount of nitrogen removed in the yield

    yield_P = Amount of phosphorus removed in the yield

    residue = Material in the residue pool for the top 10mm of soil on current
              day (kg/ha)


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

from math import exp


def update_all(crop_type, time, soil):
    """Runs all the yield calculations

    Inputs:
        crop_type
        time
        soil
    """

    calc_HI_max(crop_type)
    calc_HI_act(crop_type)
    calc_yield_max(crop_type)
    calc_yield_act(crop_type)
    calc_nutrient_removal(crop_type)
    calc_residue(crop_type, time, soil)


def calc_HI_max(crop_type):
    """Calculates max potential harvest index for a given day.
       "pseudocode_crop" C.10.C.1

    Inputs:
        crop_type
    """

    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - (10 * crop_type.fr_PHU))
    crop_type.HI_max = crop_type.HI_opt * top / bottom


def calc_HI_act(crop_type):
    """Calculates the actual harvest index (HI_actual).
       "pseudocode_crop" C.10.C.1

    Inputs:
        crop_type
    """

    term1 = crop_type.HI_max - crop_type.HI_min
    exp_part = exp(6.13 - (0.883 * crop_type.gamma_wu))
    term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)

    crop_type.HI_actual = term1 * term2 + crop_type.HI_min


def calc_yield_max(crop_type):
    """Calculates maximum crop yield at harvest.
       "pseudocode_crop" C.10.D.1

    Inputs:
        crop_type
    """

    crop_type.yield_max = crop_type.bio_AG * crop_type.HI_actual


def calc_yield_act(crop_type):
    """Calculates actual crop yield at harvest.
       "pseudocode_crop" C.10.E.1

    Inputs:
        crop_type
    """

    crop_type.yield_actual = crop_type.yield_max * crop_type.harvest_eff

    crop_type.yield_annual += crop_type.yield_actual


def calc_nutrient_removal(crop_type):
    """Calculates the amount of nitrogen and phosphorus removed in the yield.
       "pseudocode_crop" C.10.F.1/2

    Inputs:
        crop_type
    """

    crop_type.yield_N = crop_type.fr_N * crop_type.yield_actual
    crop_type.yield_P = crop_type.fr_P * crop_type.yield_actual


def calc_residue(crop_type, time, soil):
    """Updates the current residue.
       "pseudocode_crop" C.10.G.1/4/5

    Inputs:
        crop_type
        time
        soil
    """

    d_residue = 0
    if time.day == crop_type.kill_day or crop_type.crop_type == 'annual':
        d_residue = crop_type.biomass_actual - crop_type.yield_actual
        kill(crop_type, soil)
    else:
        bio_frac = crop_type.yield_actual / crop_type.biomass_actual
        cut(crop_type, bio_frac)
    soil.residue += d_residue


def kill(crop_type, soil):
    """Kills the crop
       "pseudocode_crop" C.10.G.4

    Inputs:
        crop_type
        soil
    """

    soil.tillage_day = True

    crop_type.accumulated_HU = 0
    crop_type.prev_accumulated_HU = 0

    crop_type.fr_PHU = 0
    crop_type.prev_fr_PHU = 0

    crop_type.LAI_actual = 0
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
    crop_type.growing = False


def cut(crop_type, bio_frac):
    """Cuts the crop without killing it
       "pseudocode_crop" C.10.G.2/3

    Inputs:
        crop_type
        bio_frac: fraction of biomass removed during harvest
    """

    crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)

    crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)
    crop_type.fr_LAI_max = 0

    crop_type.biomass_actual -= crop_type.yield_actual

    crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)
    crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)

    crop_type.ET_annual = 0
