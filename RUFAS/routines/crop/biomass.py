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

    dBiomass_max = Maximum potential biomass increase on current day

    dBiomass_actual = Actual increase in total plant biomass on a given day (kg ha^-1)

    biomass_actual = Total plant biomass on a given day

    gamma_reg = Plant growth factor


CropType values updated by update_all():

    dBiomass_max
    dBiomass_actual
    prev_biomass_actual
    biomass_actual
"""
###############################################################################

from math import exp


#
# This function updates all biomass information
#
def update_all(crop_type, time, weather):

    # update biomass values
    calc_actual_Biomass(crop_type, time, weather)


#
# Calculate current actual biomass.
# "pseudocode_crop" C.9.A.2/3
#
def calc_actual_Biomass(crop_type, time, weather):
    H_phosyn = calc_intercepted_radiation(crop_type, time, weather)

    # C.9.A.2
    crop_type.dBiomass_max = crop_type.RUE * H_phosyn

    # C.9.A.3
    crop_type.dBiomass_actual = crop_type.dBiomass_max * crop_type.gamma_reg

    # Save value as previous day's value
    crop_type.prev_biomass_actual = crop_type.biomass_actual

    in_growing_period = crop_type.start_date <= time.day <= crop_type.harvest_date and not crop_type.dormancy

    # Update current actual biomass
    if in_growing_period:
        crop_type.biomass_actual += crop_type.dBiomass_actual
    else:
        crop_type.biomass_actual = 0


#
# Calculates amount of intercepted photosynthetically active radiation
# on a given day (MJ m^-2).
# "pseudocode_crop" C.9.A.1
#
def calc_intercepted_radiation(crop_type, time, weather):
    H_day = weather.radiation[time.year - 1][time.day - 1]
    return 0.5 * H_day * (1 - exp(-1 * crop_type.kl * crop_type.LAI_actual))
