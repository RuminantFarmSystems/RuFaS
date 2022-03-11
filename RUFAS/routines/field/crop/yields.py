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

    ET_annual = Sum of actual evapotranspiration from day 1 up to today (mm H2O)

    ET_max_annual = Sum of potential evapotranspiration from day 1 up to today (mm H2O)

    HI_actual = Actual harvest index

    HI_opt = Potential harvest for the plant at maturity given ideal growing
             conditions

    bio_AG = Above ground biomass (kg/ha)

    harvest_eff = Efficiency of the harvest operation, i.e. fraction of yield
                  biomass removed by the harvesting equipment.

    yield_max = maximum crop yield at harvest (kg/ha)

    yield_actual = Actual crop yield at harvest (kg/ha)

    N_yield = Amount of nitrogen removed in the yield

    P_yield = Amount of phosphorus removed in the yield

    residue = Material in the residue pool for the top 10mm of soil on current
              day (kg/ha)


CropType values updated by update_all():

    gamma_wu
    HI_max
    bio_AG
    HI_actual
    yield_max
    yield_actual
    N_yield
    P_yield
    residue
"""

from math import exp


def update_all(soil, crop_type, field_management, time):
    """
    Description:
        Runs all the yield calculations

    Args:
        soil: an instance of the Soil class specified in soil.py representing
            the current state of the soil profile
        crop_type: an instance of a crop class
        field_management: an instance of the FieldManagement class
            specified in field_management.py
        time: an instance of the Time class specified in classes.py
    """


    calc_HI_max(crop_type)
    calc_HI_act(crop_type)

    if crop_type.fr_PHU > 1.0:
        calc_dry_down(crop_type)

    calc_yield_max(crop_type)
    calc_yield_act(crop_type)
    calc_harvest_quality(crop_type)
    calc_nutrient_removal(crop_type)
    calc_residue(soil, crop_type, field_management, time)
    calc_quality_assessment(crop_type)


#
# Calculates max potential harvest index for a given day.
# "pseudocode_crop" C.10.C.1
#
def calc_HI_max(crop_type):
    """
    Description:
        Calculates max potential harvest index for a given day.
        "pseudocode_crop" C.10.C.1

    Args:
        crop_type
    """

    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - (10 * crop_type.fr_PHU))
    crop_type.HI_max = crop_type.HI_opt * top / bottom


def calc_HI_act(crop_type):
    """
    Description:
        Calculates the actual harvest index (HI_actual).
        "pseudocode_crop" C.10.C.1

    Args:
        crop_type
    """

    term1 = crop_type.HI_max - crop_type.HI_min
    exp_part = exp(6.13 - (0.883 * crop_type.gamma_wu))
    term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)

    crop_type.HI_actual = term1 * term2 + crop_type.HI_min


def calc_dry_down(crop_type):
    # TODO: stand in for more sophisticated dry down method
    crop_type.bio_AG -= (crop_type.bio_AG * crop_type.biomass_dry_down_percent)


#
# Calculates maximum crop yield at harvest.
# "pseudocode_crop" C.10.D.1
#
def calc_yield_max(crop_type):
    """
    Description:
        Calculates maximum crop yield at harvest.
        "pseudocode_crop" C.10.D.1

    Args:
        crop_type
    """

    crop_type.yield_max = crop_type.bio_AG * crop_type.HI_actual


def calc_yield_act(crop_type):
    """
    Description:
        Calculates actual crop yield at harvest.
        "pseudocode_crop" C.10.E.1

    Args:
        crop_type
    """

    crop_type.yield_actual = crop_type.yield_max * crop_type.harvest_eff


def calc_quality_assessment(crop_type):
    """
    Description:
        TODO: Stand in for more sophisticated method
        Assesses quality of feed at harvest
        "Feed Inventory Pseudocode" F.1.1
    Args:
        crop_type: the crop for which a quality is being assessed
    """
    crop_type.harvest_quality = 'mid_mature'
    crop_type.feed_id = crop_type.feed_id
    if crop_type.crop_name.startswith('corn'):
        if crop_type.harvest_quality == 'immature':
            crop_type.feed_id = '35g'
            crop_type.NDF_harvest_percent = 0.541
        elif crop_type.harvest_quality == 'mid_mature':
            crop_type.feed_id = '36g'
            crop_type.NDF_harvest_percent = 0.45
        elif crop_type.harvest_quality == 'mature':
            crop_type.feed_id = '37g'
            crop_type.NDF_harvest_percent = 0.445


def calc_nutrient_removal(crop_type):
    """
    Description:
        Calculates the amount of nitrogen and phosphorus removed in the yield.
        "pseudocode_crop" C.10.F.1/2

    Args:
        crop_type
    """

    crop_type.N_yield = crop_type.fr_N * crop_type.yield_actual
    crop_type.P_yield = crop_type.fr_P * crop_type.yield_actual


def calc_residue(soil, crop_type, field_management, time):
    """
    Description:
        Updates the current residue.
        "pseudocode_crop" C.10.H.1/4/5

    Args:
        soil
        crop_type
        field_management
        time
    """
    # for carbon, needs to be calculated only at harvest
    # C.3.A.4
    crop_type.bio_BG = crop_type.fr_root * crop_type.biomass_actual
    soil.soil_layers[0].tillage_percent = 0.55
    # lignin residue reset at harvest
    soil.AG_lignin_res_percent = 17  # TODO
    soil.BG_lignin_res_percent = 17  # TODO

    d_residue = 0
    if time.day == crop_type.kill_day or crop_type.crop_type == 'annual':
        d_residue = crop_type.biomass_actual - crop_type.yield_actual
        kill(crop_type, field_management, time)
    else:
        bio_frac = crop_type.yield_actual / crop_type.biomass_actual
        cut(crop_type, bio_frac)

    soil.residue += d_residue

    soil.residue_harvest = soil.residue


def calc_harvest_quality(crop_type):
    """
    Description:
        # TODO: Stand in for more sophisticated method
        Calculate quality of yield for grouping in feed storage
        "pseudocode_crop" C.10.G
    Args:
        crop_type
    """
    crop_type.harvest_quality = "good"


def kill(crop_type, field_management, time):
    """
    Description:
        Kills the crop.
        NOTE: Any day-of-yield values reset here will be reported to the output
        handler as 0. To reset after reporting see crop.daily_reset()
        "pseudocode_crop" C.10.H.4

    Args:
        crop_type
        field_management
        time
    """
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

    crop_type.ET_annual = 0

    crop_type.planted = False
    crop_type.growing = False
    crop_type.killed = True

    # FM.2.2
    till_management = field_management.managed_applications['tillage']
    if (time.calendar_year, -1) in till_management.applications:
        till_management.schedule_application(time)


def cut(crop_type, bio_frac):
    """
    Description:
        Cuts the crop without killing it
        "pseudocode_crop" C.10.H.2/3

    Args:
        crop_type
        bio_frac: fraction of biomass removed during the cut
    """

    crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)
    crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU

    crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)
    crop_type.fr_LAI_max = 0

    crop_type.biomass_actual -= crop_type.yield_actual

    crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)
    crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)

    crop_type.ET_annual = 0
