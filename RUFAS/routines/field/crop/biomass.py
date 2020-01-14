"""
RUFAS: Ruminant Farm Systems Model

File name: biomass.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the biomass values of a crop_type. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

CropType attribute definitions:

    H_day = incident total solar (MJ m^-2)

    kl = light extinction coefficient

    LAI = Leaf Area Index

    H_phosyn = Amount of intercepted photosynthetically active radiation on a
               given day. (MJ m^-2)

    RUE = Crop-specific radiation use efficiency (10^-1 g/MJ)

    d_biomass_max = Maximum potential biomass increase on current day

    d_biomass_actual = Actual increase in total plant biomass on a given day (kg/ha)

    biomass_actual = Total plant biomass on a given day

    gamma_reg = Plant growth factor


CropType values updated by update_all():

    d_biomass_max
    d_biomass_actual
    prev_biomass_actual
    biomass_actual
"""

from math import exp


def update_all(crop_type, soil, time, weather):
    """This function updates all biomass information

    Inputs:
        crop_type
        soil
        time
        weather
    """

    # update biomass values
    calc_act_biomass(crop_type, time, weather)

    calc_bio_AG(crop_type)

    calc_gamma_wu(crop_type, soil)


def calc_act_biomass(crop_type, time, weather):
    """Calculates current actual biomass
       "pseudocode_crop" C.9.A.2/3

    Inputs:
        crop_type
        time
        weather
    """

    H_phosyn = calc_intercepted_radiation(crop_type, time, weather)

    # C.9.A.2
    crop_type.d_biomass_max = crop_type.RUE * H_phosyn

    # C.9.A.3
    crop_type.d_biomass_actual = crop_type.d_biomass_max * crop_type.gamma_reg

    # Save value as previous day's value
    crop_type.prev_biomass_actual = crop_type.biomass_actual

    # Update current actual biomass
    crop_type.biomass_actual += crop_type.d_biomass_actual


def calc_intercepted_radiation(crop_type, time, weather):
    """Calculates amount of intercepted photosynthetically active radiation
       on a given day (MJ m^-2).
       "pseudocode_crop" C.9.A.1

    Inputs:
        crop_type
        time
        weather
    Returns:
        int: intercepted radiation
    """

    H_day = weather.radiation[time.year - 1][time.day - 1]
    return 0.5 * H_day * (1 - exp(-1 * crop_type.kl * crop_type.LAI_actual))


def calc_bio_AG(crop_type):
    """Calculates aboveground biomass.
       "pseudocode_crop" C.9.B.1

    Inputs:
        crop_type
    """

    crop_type.bio_AG = (1 - crop_type.fr_root) * crop_type.biomass_actual


def calc_gamma_wu(crop_type, soil):
    """Calculates water deficiency factor (AKA gamma_wu).
       "pseudocode_crop" C.9.C.1

    Inputs:
        crop_type
        soil
    """

    if soil.ET_max_annual == 0:
        return 0

    soil.ET_annual = soil.evap_annual + soil.trans_annual
    crop_type.gamma_wu = 100 * (soil.ET_annual / soil.ET_max_annual)

