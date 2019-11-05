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

    Tconc = time of concentration (h)

    Length = slope length of field (m)

    n = manning's roughness coefficient

    slope = field slope (m/m)

    R = daily rainfall(mm)

    alpha = fraction of daily rain during time of concentration

    alpha05 = fraction of daily rain in 1/2 hour of highest intensity

    Fcsand = gives low factors for soils with high sand content and high values
                for soils with low sand content

    Fcl_si = gives low factors for soils with high clay to silt ratios

    Forgc = reduces soil erodibility for soils with high organic carbon content

    Fsand = reduces soil erodibility for soils with high sand contents

    Cover = amount of residue and growing biomass covering the soil surface (kg/ha)

    Lhill = hillslope length (m)

    Alphahill = angle of the hillslope defined arctan(slope) (m/m)


Soil values updated by calling update_all():
    sedimentYield


"""
###############################################################################

from math import exp, log, atan, sin


#
# This function updates all soil erosion information
#
def update_all(soil, crop, weather, time):

    calc_sed(soil, crop, weather, time)


#
# Calculates sed, sediment yield on a given day (metric tons)
# "pseudocode_soil" S.3.A.1/17
#
def calc_sed(soil, crop, weather, time):
    runoff = soil.runoff
    peak_runoff = calc_peak_runoff(soil, weather, time)
    K = calc_K(soil)
    C = calc_C(soil, crop)
    P = soil.practiceFactor
    LS = calc_LS(soil)

    sed = 11.8 * ((runoff * peak_runoff) ** 0.56) * K * C * P * LS

    # Sediment yield is adjusted for snow on the range day < 60 or day > 350
    # "pseudocode_soil" S.3.A.17
    if time.day < 60 or time.day > 350:
        exp_part = exp(3 * 20 / 25.4)
        sed = sed / exp_part

    soil.sedimentYield = sed


#
# Calculates the peak runoff rate (m^3/sec)
# "pseudocode_soil" S.3.A.2/3
#
def calc_peak_runoff(soil, weather, time):
    peak_runoff = 0.0
    R = weather.rainfall[time.year-1][time.day-1]
    if R != 0:

        # "pseudocode_soil" S.3.A.3
        runoff = soil.runoff
        RC = runoff / R

        I = calc_I(soil, weather, time)
        Area = soil.fieldSize

        peak_runoff = (RC * I * Area) / 3.6

    return peak_runoff


#
# Calculates I, the rainfall intensity (mm/hr)
# "pseudocode_soil" S.3.A.4
#
def calc_I(soil, weather, time):
    Tconc = calc_Tconc(soil)
    Rtc = calc_Rtc(soil, weather, time)

    return Rtc / Tconc


#
# Calculates Tconc (the time of concentration (h))
# "pseudocode_soil" S.3.A.5
#
def calc_Tconc(soil):
    Length = soil.slopeLength ** 0.6
    n = soil.manning ** 0.6
    slope = soil.fieldSlope ** 0.3

    return (Length * n) / (18 * slope)


#
# Calculates Rtc, the amount of rain during time of concentration (mm)
# "pseudocode_soil" S.3.A.6
#
def calc_Rtc(soil, weather, time):
    alpha = calc_alpha(soil, weather, time)
    R = weather.rainfall[time.year-1][time.day-1]

    return alpha * R


#
# Calculates alpha, the fraction of daily rain during the time of concentration
# "pseudocode_soil" S.3.A.7
#
def calc_alpha(soil, weather, time):
    Tconc = calc_Tconc(soil)
    alpha05 = calc_alpha05(weather, time)

    log_part = log(1 - alpha05)
    exp_part = exp(2 * Tconc * log_part)

    return 1 - exp_part


#
# Calculates alpha05, the fraction of daily rain in the 1/2 hour of highest
# intensity.
# "pseudocode_soil" S.3.A.8
#
def calc_alpha05(weather, time):
    R = weather.rainfall[time.year-1][time.day-1]

    exp_part = exp(-125 / (R + 5))

    return (0.02083 + (1 - exp_part)) / 2


#
# Calculates the soil erodibility factor K.
# "pseudocode_soil" S.3.A.9
#
def calc_K(soil):
    Fcsand = calc_Fcsand(soil)
    Fcl_si = calc_Fcl_si(soil)
    Forgc = calc_Forgc(soil)
    Fsand = calc_Fsand(soil)

    return Fcsand * Fcl_si * Forgc * Fsand


#
# Calculates Fcsand. Fcsand gives low factors for soils with high sand contents
# and high values for soils with little sand when calculating K
# "pseudocode_soil" S.3.A.10
#
def calc_Fcsand(soil):
    sand = soil.sand
    silt = soil.silt

    exp_part = exp(-0.256 * sand * (1 - (silt / 100)))

    return 0.2 + 0.3 * exp_part


#
# Calculates Fcl_si. Fcl_si gives low factors for soils with high clay to silt
# ratios when calculating K
# "pseudocode_soil" S.3.A.11
#
def calc_Fcl_si(soil):
    silt = soil.silt
    clay = soil.soil_layers[0].clay

    return (silt / (clay + silt)) ** 0.3


#
# Calculates Forgc. Forgc reduces soil erodibility for soils with high organic
# carbon content when calculating K
# "pseudocode_soil" S.3.A.12
#
def calc_Forgc(soil):
    orgC = soil.soil_layers[0].orgC

    exp_part = exp(3.72 - 2.95 * orgC)

    return 1 - ((0.25 * orgC) / (orgC + exp_part))


#
# Calculates Fsand. Fsand reduces soil erodibility for soils with high sand
# contents when calculating K
# "pseudocode_soil" S.3.A.13
#
def calc_Fsand(soil):
    sand = soil.sand

    exp_part = exp(-5.51 + 22.9 * (1 / (sand / 100)))

    return 1 - (0.7 * (1 - sand / 100) / ((1 - sand / 100) + exp_part))


#
# Calculates the cover and management factor, C, as the ratio of soil loss from
# land cropped under specified conditions to loss from clean-tilled, continuous
# fallow. The minimum value for C is estimated at 0.05
# "pseudocode_soil" S.3.A.14
#
def calc_C(soil, crop):
    bio_AG = crop.current_crop.bio_AG
    residue = soil.residue
    Cover = bio_AG + residue

    l1 = log(0.8)
    l2 = log(0.05)
    exp_part = exp(-0.00115 * Cover)

    return exp((l1 - l2) * exp_part + l2)


#
# Calculates the topographic factor LS (the expected ratio of soil loss per
# unit area from a 22.1-m length of uniform 9 percent slope under identical
# conditions
# "pseudocode_soil" S.3.A.15
#
def calc_LS(soil):
    Lhill = soil.slopeLength
    Alphahill = atan(soil.fieldSlope)
    m = calc_m(soil)

    sin2_Alphahill = sin(Alphahill) ** 2
    sin_Alphahill = sin(Alphahill)

    return ((Lhill / 22.1) ** m) * \
           (65.41 * sin2_Alphahill + 4.56 * sin_Alphahill + 0.065)


#
# Calculates the exponent m as a function of field slope
# "pseudocode_soil" S.3.A.16
#
def calc_m(soil):
    slope = soil.fieldSlope

    exp_part = exp(-35.835 * slope)

    return 0.6 * (1 - exp_part)
