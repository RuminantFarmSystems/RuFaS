"""
RUFAS: Ruminant Farm Systems Model

File name: heat_units.py

Author(s): Andy Achenreiner, achenreiner@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating a CropType's fr_PHU (fraction of PHU accumulated by
             current day). Since this submodule does not depend on values
             calculated in other crop submodules, heat_units.update_all() should
             be the first function called in the daily_crop_routine.

CropType attribute definitions:

    * Note that all temperatures listed below are in degrees Celsius

    T_min = Minimum temperature on current day

    T_max = Maximum temperature on current day

    T_base_min = Crop-specific minimum temperature required for growth

    T_base_max = Crop-specific maximum temperature required to sustain growth.

    T_HU_min = Minimum heat unit temperature on current day

    T_HU_max = Maximum heat unit temperature on current day

    T_HU = Mean heat unit temperature on current day

    HU = Available heat units on current day

    prev_accumulated_HU = Accumulated_HU leading up to today

    accumulated_HU = Heat units accumulated up to and including today

    PHU = Crop-specific total heat units required for maturity

    prev_fr_PHU = Fraction of PHU accumulated up to today

    fr_PHU = Fraction of PHU accumulated including today

CropType values updated by calling calculate_frPHU():

    prev_accumulated_HU
    accumulated_HU
    prev_fr_PHU
    fr_PHU
"""
################################################################################


#
# This function calls the functions necessary to update the current heat unit
# information.
#
def update_all(crop_type, weather, time):
    calculate_fr_PHU(crop_type, weather, time)


#
# This function calculates the fraction of PHU accumulated up to and including
# today. The equations used for this part can be found in
# "pseudocode_crop" C.2.B.1
#
def calculate_fr_PHU(crop_type, weather, time):

    T_min = weather.T_min[time.year - 1][time.day - 1]
    T_max = weather.T_max[time.year - 1][time.day - 1]

    T_HU_min = calc_T_HU_min(crop_type, T_min)
    T_HU_max = calc_T_HU_max(crop_type, T_max)
    HU = calc_HU(crop_type, T_HU_min, T_HU_max)

    crop_type.prev_accumulated_HU = crop_type.accumulated_HU

    crop_type.accumulated_HU = crop_type.accumulated_HU + HU

    crop_type.prev_fr_PHU = crop_type.fr_PHU

    # Calculate accumulated fraction of potential Heat Units
    # C.2.B.1

    crop_type.fr_PHU = crop_type.accumulated_HU / crop_type.PHU


#
# Calculates minimum heat unit temperature on current day.
# "pseudocode_crop" C.2.A.3
#
def calc_T_HU_min(crop_type, T_min):
    if T_min < crop_type.T_base_min:
        return crop_type.T_base_min
    else:
        return T_min


#
# Calculates maximum heat unit temperature on current day.
# "pseudocode_crop" C.2.A.4
#
def calc_T_HU_max(crop_type, T_max):
    if T_max > crop_type.T_base_max:
        return crop_type.T_base_max
    else:
        return T_max


#
# Calculates available heat units on current day.
# # "pseudocode_crop" C.2.A.1/2
#
def calc_HU(crop_type, T_HU_min, T_HU_max):
    # 2.A.2
    T_HU = (T_HU_min + T_HU_max) / 2

    # "pseudocode_crop" C.2.A.1
    if T_HU < crop_type.T_base_min:
        return 0.0
    else:
        return T_HU - crop_type.T_base_min
