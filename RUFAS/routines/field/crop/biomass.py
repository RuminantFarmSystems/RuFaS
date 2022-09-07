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


def update_all(soil, crop_type, weather, time):
    """
    Description:
        Called from crop.py, This function updates all biomass information

    Args:
        soil: the current instance of soil in which the crop is growing
        crop_type: an instance of a crop class
        weather: an instance of the Weather class specified in classes.py,
            contains environmental information
        time: an instance of the Time class specified in classes.py
    """

    # update biomass values
    calc_act_biomass(crop_type, weather, time)

    calc_bio_AG(crop_type)

    calc_gamma_wu(soil, crop_type)


def calc_act_biomass(crop_type, weather, time):
    """
    Description:
        Calculates current actual biomass
       "pseudocode_crop" C.9.A.2/3

    Args:
        crop_type: instance of Crop type subclass
        weather: instance of Weather class
        time: instance of Time class
    """

    H_phosyn = calc_intercepted_radiation(crop_type, weather, time)

    # C.9.A.2
    crop_type.d_biomass_max = crop_type.RUE * H_phosyn

    # C.9.A.3
    crop_type.d_biomass_actual = crop_type.d_biomass_max * crop_type.gamma_reg
    print(crop_type.prev_biomass_actual)

    # Save value as previous day's value
    crop_type.prev_biomass_actual = crop_type.biomass_actual

    # Update current actual biomass
    crop_type.biomass_actual += crop_type.d_biomass_actual


def calc_intercepted_radiation(crop_type, weather, time):
    """
    Description:
        Calculates amount of intercepted photosynthetically active radiation
        on a given day (MJ m^-2).
        "pseudocode_crop" C.9.A.1

    Args:
        crop_type: instance of Crop type subclass
        weather: instance of Weather class
        time: instance of Time class

    Returns:
        int: intercepted radiation
    """

    H_day = weather.radiation[time.year - 1][time.day - 1]
    return 0.5 * H_day * (1 - exp(-1 * crop_type.kl * crop_type.LAI_actual))


def calc_bio_AG(crop_type):
    """
    Description:
        Calculates above ground biomass.
        "pseudocode_crop" C.9.B.1

    Args:
        crop_type: instance of Crop type subclass
    """

    crop_type.bio_AG = (1 - crop_type.fr_root) * crop_type.biomass_actual


def calc_gamma_wu(soil, crop_type):
    """
    Description:
        Calculates water deficiency factor (AKA gamma_wu).
        "pseudocode_crop" C.9.C.1

    Args:
        soil: instance of Soil class
        crop_type: instance of Crop type subclass
    """

    if soil.ET_max_annual == 0:
        return 0

    soil.ET_annual = soil.evap_annual + soil.trans_annual
    crop_type.gamma_wu = 100 * (soil.ET_annual / soil.ET_max_annual)
