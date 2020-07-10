"""
RUFAS: Ruminant Farm Systems Model

File name: yields.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu
            William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the yield values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

"""
from math import exp


# Runs yield calculations
def update_all(soil, crop_type, field_management, weather, time):

    calc_HI_max(crop_type)
    calc_HI_act(crop_type)

    if crop_type.fr_PHU > 1.0:
        calc_dry_down(crop_type)

    calc_yield_max(crop_type)
    calc_yield_act(crop_type)
    calc_nutrient_removal(crop_type)
    calc_residue(soil, crop_type, field_management, weather, time)
    calc_quality_assessment(crop_type)
    calc_DM_yield(crop_type)
    calc_NDF_yield(crop_type)


# Calculates max potential harvest index for a given day.
# "pseudocode_crop" C.10.C.1
def calc_HI_max(crop_type):
    top = 100 * crop_type.fr_PHU
    bottom = 100 * crop_type.fr_PHU + exp(11.1 - (10 * crop_type.fr_PHU))
    crop_type.HI_max = crop_type.HI_opt * top / bottom


#
# Calculates the actual harvest index (HI_actual).
# "pseudocode_crop" C.10.C.1
#
def calc_HI_act(crop_type):

    term1 = crop_type.HI_max - crop_type.HI_min
    exp_part = exp(6.13 - (0.883 * crop_type.gamma_wu))
    term2 = crop_type.gamma_wu / (crop_type.gamma_wu + exp_part)

    crop_type.HI_actual = term1 * term2 + crop_type.HI_min


def calc_dry_down(crop_type):
    # TODO: stand in for more sophisticated dry down method
    crop_type.bio_AG -= (crop_type.bio_AG * crop_type.biomass_dry_down_perc)


#
# Calculates maximum crop yield at harvest.
# "pseudocode_crop" C.10.D.1
#
def calc_yield_max(crop_type):
    crop_type.yield_max = crop_type.bio_AG * crop_type.HI_actual


#
# Calculates actual crop yield at harvest.
# "pseudocode_crop" C.10.E.1
#
def calc_yield_act(crop_type):
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
            crop_type.NDF_harvest_perc = 0.541
        elif crop_type.harvest_quality == 'mid_mature':
            crop_type.feed_id = '36g'
            crop_type.NDF_harvest_perc = 0.45
        elif crop_type.harvest_quality == 'mature':
            crop_type.feed_id = '37g'
            crop_type.NDF_harvest_perc = 0.445


def calc_DM_yield(crop_type):
    crop_type.DM_yield = crop_type.yield_actual * crop_type.DM_harvest_perc


def calc_NDF_yield(crop_type):
    crop_type.NDF_yield = crop_type.yield_actual * crop_type.NDF_harvest_perc


#
# Calculates the amount of nitrogen and phosphorus removed in the yield.
# "pseudocode_crop" C.10.F.1/2
#
def calc_nutrient_removal(crop_type):
    crop_type.N_yield = crop_type.fr_N * crop_type.yield_actual
    crop_type.P_yield = crop_type.fr_P * crop_type.yield_actual


#
# Updates the current residue.
# "pseudocode_crop" C.10.G.1/4/5
#
def calc_residue(soil, crop_type, field_management, weather, time):
    d_residue = 0
    if time.day == crop_type.kill_day or crop_type.crop_type == 'annual':
        d_residue = crop_type.biomass_actual - crop_type.yield_actual
        kill(soil, crop_type, field_management, weather, time)
    else:
        bio_frac = crop_type.yield_actual / crop_type.biomass_actual
        cut(crop_type, bio_frac)
    soil.residue += d_residue


#
# Kills the crop
# "pseudocode_crop" C.10.G.4
#
def kill(soil, crop_type, field_management, weather, time):

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
    crop_type.harvested = True

    till_management = field_management.managed_applications['tillage']
    if (time.cal_year, -1) in till_management.applications:
        till_management.schedule_application(time)


#
# Cuts the crop without killing it
# "pseudocode_crop" C.10.G.2/3
#
def cut(crop_type, bio_frac):
    crop_type.accumulated_HU = crop_type.accumulated_HU * (1 - bio_frac)

    crop_type.LAI_actual = crop_type.LAI_actual * (1 - bio_frac)
    crop_type.fr_LAI_max = 0

    crop_type.biomass_actual -= crop_type.yield_actual

    crop_type.bio_P = crop_type.bio_P * (1 - bio_frac)
    crop_type.bio_N = crop_type.bio_N * (1 - bio_frac)

    crop_type.ET_annual = 0
