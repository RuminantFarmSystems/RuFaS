"""
RUFAS: Ruminant Farm Systems Model

File name: soil_water.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil water in the profile at the end of a given day.
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.
"""


def update_all(soil, weather, time):
    """
    Description:
        This function calls all the necessary functions to update and track
        soil water pools

    Args:
        soil: instance of the Soil class specified in soil.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    update_profile_SW(soil, weather, time)


def update_profile_SW(soil, weather, time):
    """
    Description:
        Tracks and updates soil water pools based on calculated fluxes.
        Currently, all soil water transformations occur at the end of the day
        and are limited at saturation and wilting point. Percolation accounts
        for any excess flux.

    Args:
        soil
        weather
        time
    """

    soil.trans = 0.0
    soil.evap = 0.0
    soil.ET_act = 0.0

    profile_SW = 0
    percolation = 0
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]

        SW = layer.soil_water
        WP = layer.wilting_water
        SAT = layer.sat_water

        percolation = layer.percolation
        evap = layer.evap
        trans = layer.trans_act
        I = soil.infiltration

        if x == 0:
            percolation_in = I
        else:
            percolation_in = soil.soil_layers[x - 1].percolation

        SW = SW + percolation_in - evap - percolation - trans

        if SW < WP:
            layer.percolation -= WP - SW
        SW = max(WP, SW)
        if SW > SAT:
            layer.percolation += SW - SAT
        SW = min(SAT, SW)

        profile_SW += SW
        soil.trans += trans
        soil.evap += evap
        soil.ET_act += (evap + trans)

        layer.soil_water = SW
        soil.soil_layers[x] = layer

    soil.drainage = percolation
    soil.delta_SW = profile_SW - soil.profile_SW
    soil.profile_SW = profile_SW

    R = weather.rainfall[time.year - 1][time.day - 1] + weather.irrigation[time.year - 1][time.day - 1]

    soil.p_act = R
    soil.p_calc = soil.delta_SW + soil.ET_act + soil.drainage + soil.runoff

    soil.water_balance_difference = soil.p_act - soil.p_calc


def update_annual_SW(soil):
    soil.ET_max_annual += soil.ET_max

    soil.drainage_annual += soil.drainage
    soil.runoff_annual += soil.runoff
    soil.trans_annual += soil.trans
    soil.evap_annual += soil.evap
    soil.ET_annual += soil.ET_act

    soil.p_act_annual += soil.p_act
