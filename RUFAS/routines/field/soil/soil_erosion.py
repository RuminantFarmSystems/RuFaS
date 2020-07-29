"""
RUFAS: Ruminant Farm Systems Model

File name: soil_erosion.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil erosion on a given day. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

Soil attribute definitions

    sed = sediment yield on a given day (metric tons)

    runoff = surface runoff volume (m^3)

    peak_runoff = peak runoff rate (m^3/sec)

    K = USLE soil erodibility factor (Mg MJ^-1mm^-1)

    C = USLE cover and management factor >= 0.05

    P = USLE support practice factor (user defined)

    LS = USLE topographic factor

    RC = Runoff coefficient

    I = rainfall intensity (mm/hr)

    Area = field size (ha)

    Rtc = rain amount during time of concentration (mm)

    T_conc = time of concentration (h)

    length = slope length of field (m)

    n = manning's roughness coefficient

    slope = field slope (m/m)

    R = daily rainfall(mm)

    alpha = fraction of daily rain during time of concentration

    alpha_05 = fraction of daily rain in 1/2 hour of highest intensity

    Fc_sand = gives low factors for soils with high sand content and high values
                for soils with low sand content

    Fcl_si = gives low factors for soils with high clay to silt ratios

    F_org_C = reduces soil erodibility for soils with high organic carbon content

    F_sand = reduces soil erodibility for soils with high sand contents

    Cover = amount of residue and growing biomass covering the soil surface (kg/ha)

    L_hill = hill slope length (m)

    alpha_hill = angle of the hill slope defined arctan(slope) (m/m)
"""

from math import exp, log, atan, sin


def update_all(soil, crop, weather, time):
    """
    Description:
        Updates all soil erosion information

    Args:
        soil: instance of the Soil class specified in soil.py
        crop: instance of the Crop class specified in crop.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    calc_sed(soil, crop, weather, time)


def calc_sed(soil, crop, weather, time):
    """
    Description:
        Calculates sed, sediment yield on a given day (metric tons)
        "pseudocode_soil" S.3.A.1/17

    Args:
        soil
        crop
        weather
        time
    """

    runoff = soil.runoff
    peak_runoff = calc_peak_runoff(soil, weather, time)
    K = calc_K(soil)
    C = calc_C(soil, crop)
    P = soil.practice_factor
    LS = calc_LS(soil)

    sed = 11.8 * ((runoff * peak_runoff) ** 0.56) * K * C * P * LS

    # Sediment yield is adjusted for snow on the range day < 60 or day > 350
    # "pseudocode_soil" S.3.A.17
    # TODO: arbitrary snow flag
    if time.day < 60 or time.day > 350:
        exp_part = exp(3 * 20 / 25.4)
        sed = sed / exp_part

    soil.sed = sed


def calc_peak_runoff(soil, weather, time):
    """
    Description:
        Calculates the peak runoff rate (m^3/sec)
        "pseudocode_soil" S.3.A.2/3

    Args:
        soil
        weather
        time

    Returns:
        int: peak_runoff, the peak runoff rate on the current day (m^3/sec
    """

    R = weather.rainfall[time.year - 1][time.day - 1]

    if R == 0:
        return 0

    # "pseudocode_soil" S.3.A.3
    runoff = soil.runoff
    RC = runoff / R

    I = calc_I(soil, weather, time)
    area = soil.area

    peak_runoff = (RC * I * area) / 3.6

    return peak_runoff


def calc_I(soil, weather, time):
    """
    Description:
        Calculates I, the rainfall intensity (mm/hr)
        "pseudocode_soil" S.3.A.4

    Args:
        soil
        weather
        time

    Returns:
        int: I, rainfall intensity (mm/hr)
    """

    T_conc = calc_T_conc(soil)
    Rtc = calc_Rtc(soil, weather, time)

    return Rtc / T_conc


def calc_T_conc(soil):
    """
    Description:
        Calculates T_conc (the time of concentration (h))
        "pseudocode_soil" S.3.A.5

    Args:
        soil

    Returns:
        int: T_conc, time of greatest concentration (h)
    """

    length = soil.slope_length ** 0.6
    n = soil.manning ** 0.6
    slope = soil.field_slope ** 0.3

    return (length * n) / (18 * slope)


def calc_Rtc(soil, weather, time):
    """
    Description:
        Calculates Rtc, the amount of rain during time of concentration (mm)
        "pseudocode_soil" S.3.A.6

    Args:
        soil
        weather
        time

    Returns:
        int: Rtc, rainfall during time of concentration (mm)
    """

    alpha = calc_alpha(soil, weather, time)
    R = weather.rainfall[time.year - 1][time.day - 1]

    return alpha * R


def calc_alpha(soil, weather, time):
    """
    Description:
       Calculates alpha, the fraction of daily rain during the time of concentration
        "pseudocode_soil" S.3.A.7

    Args:
        soil
        weather
        time

    Returns:
        int: alpha, fraction of rain that occurs during time of concentration
    """

    T_conc = calc_T_conc(soil)
    alpha_05 = calc_alpha_05(weather, time)

    log_part = log(1 - alpha_05)
    exp_part = exp(2 * T_conc * log_part)

    return 1 - exp_part


def calc_alpha_05(weather, time):
    """
    Description:
        Calculates alpha_05, the fraction of daily rain in the 1/2 hour of
        highest intensity.
        "pseudocode_soil" S.3.A.8

    Args:
        weather
        time

    Returns:
        int: alpha_05, fraction of daily rain in the 1/2 hour of highest intensity
    """

    R = weather.rainfall[time.year-1][time.day-1]

    exp_part = exp(-125 / (R + 5))

    return (0.02083 + (1 - exp_part)) / 2


def calc_K(soil):
    """
    Description:
        Calculates the soil erodibility factor K.
        "pseudocode_soil" S.3.A.9

    Args:
        soil

    Returns:
        int: K, unitless soil erodibility factor
    """

    Fc_sand = calc_Fc_sand(soil)
    Fcl_si = calc_Fcl_si(soil)
    F_org_C = calc_F_org_C(soil)
    F_sand = calc_F_sand(soil)

    return Fc_sand * Fcl_si * F_org_C * F_sand


def calc_Fc_sand(soil):
    """
    Description:
        Calculates Fc_sand. Fc_sand gives low factors for soils with high sand
        contents and high values for soils with little sand when calculating K
        "pseudocode_soil" S.3.A.10

    Args:
        soil

    Returns:
        int: Fc_sand, unitless sand factor
    """

    sand = soil.sand
    silt = soil.silt

    exp_part = exp(-0.256 * sand * (1 - (silt / 100)))

    return 0.2 + 0.3 * exp_part


def calc_Fcl_si(soil):
    """
    Description:
        Calculates Fcl_si. Fcl_si gives low factors for soils with high clay to silt
        ratios when calculating K
        "pseudocode_soil" S.3.A.11

    Args:
        soil

    Returns:
        int: Fcl_si, unitless clay:silt ratio factor
    """

    silt = soil.silt
    clay = soil.soil_layers[0].clay

    return (silt / (clay + silt)) ** 0.3


def calc_F_org_C(soil):
    """
    Description:
        Calculates F_org_C. F_org_C reduces soil erodibility for soils with
        high organic carbon content when calculating K
        "pseudocode_soil" S.3.A.12

    Args:
        soil

    Returns:
        int: F_org_C, unitless organic carbon factor
    """

    org_C = soil.soil_layers[0].org_C

    exp_part = exp(3.72 - 2.95 * org_C)

    return 1 - ((0.25 * org_C) / (org_C + exp_part))


def calc_F_sand(soil):
    """
    Description:
        Calculates F_sand. F_sand reduces soil erodibility for soils with high
        sand contents when calculating K
        "pseudocode_soil" S.3.A.13

    Args:
        soil

    Returns:
        int: F_sand, unitless sand factor
    """

    sand = soil.sand

    exp_part = exp(-5.51 + 22.9 * (1 / (sand / 100)))

    return 1 - (0.7 * (1 - sand / 100) / ((1 - sand / 100) + exp_part))


def calc_C(soil, crop):
    """
    Definitions:
        Calculates the cover and management factor, C, as the ratio of soil
        loss from land cropped under specified conditions to loss from
        clean-tilled, continuous fallow. The minimum value for C is estimated
        at 0.05
        "pseudocode_soil" S.3.A.14

    Args:
        soil
        crop

    Returns:
        int: C, unitless cover and management factor
    """

    bio_AG = crop.current_crop.bio_AG
    residue = soil.residue
    Cover = bio_AG + residue

    l1 = log(0.8)
    l2 = log(0.05)
    exp_part = exp(-0.00115 * Cover)

    return exp((l1 - l2) * exp_part + l2)


def calc_LS(soil):
    """
    Description:
        Calculates the topographic factor LS (the expected ratio of soil loss
        per unit area from a 22.1-m length of uniform 9 percent slope under
        identical conditions
        "pseudocode_soil" S.3.A.15

    Args:
        soil

    Returns:
        int: LS, unitless topographic factor
    """

    L_hill = soil.slope_length
    alpha_hill = atan(soil.field_slope)
    m = calc_m(soil)

    sin2_alpha_hill = sin(alpha_hill) ** 2
    sin_alpha_hill = sin(alpha_hill)

    return ((L_hill / 22.1) ** m) * \
           (65.41 * sin2_alpha_hill + 4.56 * sin_alpha_hill + 0.065)


def calc_m(soil):
    """
    Description:
        Calculates the exponent m as a function of field slope
        "pseudocode_soil" S.3.A.16

    Args:
        soil

    Returns:
        int: m, unitless field slope exponent
    """

    slope = soil.field_slope

    exp_part = exp(-35.835 * slope)

    return 0.6 * (1 - exp_part)
