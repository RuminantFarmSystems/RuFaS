"""
RUFAS: Ruminant Farm Systems Model

File name: soil_temp.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil temperature on a given day. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             functions within this file.

Soil attribute definitions

    T_soil = soil temperature (ºC) at depth z (mm)

    L = lag coefficient, set to 0.8

    T_soil_prev_day = soil temperature (ºC) at depth z (mm) on the previous day

    df = depth factor

    T_a_air = average annual air temperature (ºC)

    T_surf = Daily soil surface temperature (ºC)

    zd = ratio of depth at the center of soil layer to damping depth

    dd = damping depth (mm)

    z = depth at the center of the soil layer

    dd_max = maximum damping depth (mm)

    scale = scaling factor for soil water

    bd = soil bulk density (g/cm^3)

    SW = total soil water in the profile (mm)

    Z_tot = total soil profile depth

    T_bare = Temperature of bare soil surface (ºC)

    T_av = Average daily temperature (ºC)

    radiate = radiation term

    H_day = daily solar radiation (MJ/m^2)

    albedo = daily albedo

    albedo_soil = soil albedo constant

    cover = soil cover index

    CV = above ground biomass and residue (kg/ha)

    bcv = weighting factor of ground cover

    SNOW = snow water content on the current day (mm)

Soil values updated by calling update_all():
    T_surf
    soil_layers.temperature
"""


from math import exp, log


def update_all(soil, crop, weather, time):
    """
    Description:
        This function updates all soil temperature information.
    """

    calc_T_surf(soil, crop, weather, time)

    calc_T_soil(soil, weather, time)


def calc_T_soil(soil, weather, time):
    """
    Description:
        Calculates the soil temperature for each layer given average annual air
        temperature. "pseudocode_soil" S.1.A.1
    """

    L = 0.8
    T_a_air = weather.T_avg_annual[time.year - 1]
    dd = calc_dd(soil)

    for x in range(len(soil.soil_layers)):

        if x == 0:
            z = soil.soil_layers[x].bottom_depth / 2
        else:
            z = (soil.soil_layers[x].bottom_depth +
                 soil.soil_layers[x - 1].bottom_depth) / 2

        # soil temperature (C) at depth z (mm) on previous day
        T_soil_prev_day = soil.soil_layers[x].temperature

        # "pseudocode_soil" S.1.A.3
        zd = z / dd

        # "pseudocode_soil" S.1.A.2
        df_exp = exp(-0.867 - 2.078 * zd)
        df = zd / (zd + df_exp)

        # "pseudocode_soil" S.1.A.1
        T_soil = (L * T_soil_prev_day) + (1 - L) * \
                (df * (T_a_air - soil.T_surf) + soil.T_surf)
        soil.soil_layers[x].temperature = T_soil


def calc_dd(soil):
    """
    Description:
        Calculates damping depth of a given soil profile as a function of soil
        water and dd_max.
        "pseudocode_soil" S.1.A.4
    """

    scale = calc_scale(soil)
    dd_max = calc_dd_max(soil)

    part_1 = log(500 / dd_max)
    part_2 = ((1 - scale)/(1 + scale)) ** 2
    exp_part = exp(part_1 * part_2)

    return dd_max * exp_part


def calc_scale(soil):
    """
    Description:
         Calculates the scaling factor for soil water in a given soil profile.
        "pseudocode_soil" S.1.A.5
    """

    SW = sum_soil_water(soil)
    Z_tot = soil.profile_depth
    bd = soil.profile_bulk_density

    return SW / ((0.356 - 0.144 * bd) * Z_tot)


def calc_dd_max(soil):
    """
    Description:
        Calculates maximum damping depth for a given soil profile.
        "pseudocode_soil" S.1.A.6
    """

    bd = soil.profile_bulk_density
    exp_part = exp(-5.63 * bd)
    return 1000 + (2500 * bd) / (bd + 686 * exp_part)


def sum_soil_water(soil):
    """
    Description:
       Calculates the sum of soil water in the profile.
    """

    total_soil_water = 0.0

    for layer in soil.soil_layers:
        total_soil_water += layer.soil_water

    return total_soil_water


def calc_T_surf(soil, crop, weather, time):
    """
    Description:
        Calculates the surface temperature as a function of the previous day's
        temperature, the amount of ground cover, and the temperature of a bare
        soil surface.
        "pseudocode_soil" S.1.A.13
    """

    T_bare = calc_T_bare(soil, crop, weather, time)
    bcv = calc_bcv(crop, time)

    soil.T_surf = (bcv * soil.soil_layers[0].temperature) + ((1 - bcv) * T_bare)


def calc_T_bare(soil, crop, weather, time):
    """
    Description:
        Calculates the temperature of a bare soil.
        "pseudocode_soil" S.1.A.7
    """
    T_av = weather.T_avg[time.year-1][time.day-1]
    radiate = calc_radiate(soil, crop, weather, time)

    return T_av + radiate * T_av


def calc_radiate(soil, crop, weather, time):
    """
    Description:
        Calculates the radiation term for the temperature of bare soil.
        "pseudocode_soil" S.1.A.8
    """

    H_day = weather.radiation[time.year-1][time.day-1]
    albedo = calc_albedo(soil, crop)

    return (H_day * (1 - albedo) - 14) / 20


def calc_albedo(soil, crop):
    """
    Description:
        Calculates the daily albedo as a function of soil type, plant cover,
        and snow cover.
        "pseudocode_soil" S.1.A.9/10
    """

    CV = crop.current_crop.bio_AG
    albedoSoil = soil.soil_albedo

    # "pseudocode_soil" S.1.A.10
    cover = exp(-0.00005 * CV)

    # "pseudocode_soil" S.1.A.9
    return 0.23 * (1 - cover) + albedoSoil * cover


def calc_bcv(crop, time):
    """
    Description:
        Calculates the weighting factor for ground cover
        "pseudocode_soil" S.1.A.11/12
    """

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
