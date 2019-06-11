'''
RUFAS: Ruminant Farm Systems Model

File name: soil_temp.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil temperature on a given day. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

Soil attribute definitions

    Tsoil = soil temperature (ºC) at depth z (mm)

    L = lag coefficient, set to 0.8

    Tsoil_prev_day = soil temperature (ºC) at depth z (mm) on the previous day

    df = depth factor

    Taair = average annual air temperature (ºC)

    Tsurf = Daily soil surface temperature (ºC)

    zd = ratio of depth at the center of soil layer to damping depth

    dd = damping depth (mm)

    z = depth at the center of the soil layer

    ddmax = maximum damping depth (mm)

    scale = scaling factor for soil water

    bd = soil bulk density (g/cm^3)

    SW = total soil water in the profile (mm)

    Ztot = total soil profile depth

    Tbare = Temperature of bare soil surface (ºC)

    Tav = Average daily temperature (ºC)

    radiate = radiation term

    Hday = daily solar radiation (MJ/m^2)

    albedo = daily albedo

    albedo_soil = soil albedo constant

    cover = soil cover index

    CV = above ground biomass and residue (kg/ha)

    bcv = weighting factor of ground cover

    SNOW = snow water content on the current day (mm)

Soil values updated by calling update_all():
    Tsurf
    listOfSoilLayers.temperature
'''
###############################################################################


from math import exp, log


#
# This function updates all soil temperature information
#
def update_all(soil, crop, weather, time):

    calc_Tsurf(soil, crop, weather, time)

    calc_Tsoil(soil, weather, time)


#
# Calculates the soil temperature for each layer given average annual air
# temperature. "pseudocode_soil" S.1.A.1
#
def calc_Tsoil(soil, weather, time):
    L = 0.8
    # Taair = weather.T_avg_annual[time.year-1]
    Taair = 8.18  # TODO: spreadsheet model fix. Note in pseudocode
    dd = calc_dd(soil)
    for x in range(0, len(soil.listOfSoilLayers)):

        if x == 0:
            z = soil.listOfSoilLayers[x].bottomDepth / 2
        else:
            z = (soil.listOfSoilLayers[x].bottomDepth +
                 soil.listOfSoilLayers[x - 1].bottomDepth) / 2

        # soil temperature (C) at depth z (mm) on previous day
        Tsoil_prev_day = soil.listOfSoilLayers[x].temperature

        # "pseudocode_soil" S.1.A.3
        zd = z / dd

        # "pseudocode_soil" S.1.A.2
        df_exp = exp(-0.867 - 2.078 * zd)
        df = zd / (zd + df_exp)

        # "pseudocode_soil" S.1.A.1
        Tsoil = (L * Tsoil_prev_day) + (1 - L) * \
                (df * (Taair - soil.Tsurf) + soil.Tsurf)
        soil.listOfSoilLayers[x].temperature = Tsoil


#
# Calculates damping depth of a given soil profile as a function of soil water and ddmax
# "pseudocode_soil" S.1.A.4
#
def calc_dd(soil):
    scale = calc_scale(soil)
    ddmax = calc_ddmax(soil)

    part_1 = log(500 / ddmax)
    part_2 = ((1 - scale)/(1 + scale)) ** 2
    exp_part = exp(part_1 * part_2)

    return ddmax * exp_part


#
# Calculates the scaling factor for soil water in a given soil profile
# "pseudocode_soil" S.1.A.5
#
def calc_scale(soil):
    SW = sum_soil_water(soil)
    Ztot = soil.profileDepth
    bd = soil.profileBulkDensity

    return SW / ((0.356 - 0.144 * bd) * Ztot)


#
# Calculates maximum damping depth for a given soil profile.
# "pseudocode_soil" S.1.A.6
#
def calc_ddmax(soil):
    bd = soil.profileBulkDensity
    exp_part = exp(-5.63 * bd)
    return 1000 + (2500 * bd) / (bd + 686 * exp_part)


#
# Calculates the sum of soil water in the profile
#
def sum_soil_water(soil):
    total_soil_water = 0.0

    for soilLayer in soil.listOfSoilLayers:
        total_soil_water += soilLayer.currentSoilWaterMM

    return total_soil_water


#
# Calculates the surface temperature as a function of the previous day's
# temperature, the amount of ground cover, and the temperature of a bare soil
# surface. "pseudocode_soil" S.1.A.13
#
def calc_Tsurf(soil, crop, weather, time):
    Tbare = calc_Tbare(soil, crop, weather, time)
    bcv = calc_bcv(crop, time)

    soil.Tsurf = (bcv * soil.listOfSoilLayers[0].temperature) + ((1 - bcv) * Tbare)


#
# Calculates the temperature of a bare soil
# "pseudocode_soil" S.1.A.7
#
def calc_Tbare(soil, crop, weather, time):
    Tav = weather.T_avg[time.year-1][time.day-1]
    radiate = calc_radiate(soil, crop, weather, time)

    return Tav + radiate * Tav


#
# Calculates the radiation term for the temperature of bare soil
# "pseudocode_soil" S.1.A.8
#
def calc_radiate(soil, crop, weather, time):
    Hday = weather.radiation[time.year-1][time.day-1]
    albedo = calc_albedo(soil, crop)

    return (Hday * (1 - albedo) - 14) / 20


#
# Calculates the daily albedo as a function of soil type, plant cover, and snow
# cover. "pseudocode_soil" S.1.A.9/10
#
def calc_albedo(soil, crop):
    CV = crop.current_crop.bio_AG
    albedoSoil = soil.soilAlbedo

    # "pseudocode_soil" S.1.A.10
    cover = exp(-0.00005 * CV)

    # "pseudocode_soil" S.1.A.9
    return 0.23 * (1 - cover) + albedoSoil * cover


#
# Calculates the weighting factor for ground cover
# "pseudocode_soil" S.1.A.11/12
#
def calc_bcv(crop, time):
    CV = crop.current_crop.bio_AG
    exp_part = exp(7.563 - 0.0001297 * (-CV))

    bcv = CV / (CV + exp_part)

    SNOW = 0
    # TODO: these time ranges for snowfall are taken from the barnyard spreadsheet model and seem largely arbitrary
    if time.day > 335 or time.day < 59:
        albedo_snow = 0.8
        SNOW = 10 * albedo_snow

    bcv_snow = (SNOW / (SNOW + exp(6.055 - 0.3002 * SNOW)))

    return max(bcv, bcv_snow)
