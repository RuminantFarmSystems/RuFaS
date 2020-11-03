"""
RUFAS: Ruminant Farm Systems Model

File name: soil_water.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil water in the profile at the end of a given day.
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

Soil attribute definitions

    runoff = daily runoff (mm H2O)

    R = daily rainfall depth (mm H2O)

    SW = soil water content of entire profile (mm H2O)

    FC = amount of water in soil profile at field capacity (mm H2O)

    WP = amount of water in the soil profile held at wilting point (mm H2O)

    percolation = the amount of water percolated to the next layer (mm H2O)

    trans_act = the amount of water lost to transpiration on a given day (mm H2O)
                (this value is taken from the crop module)
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

    update_SW(soil, weather, time)


def update_SW(soil, weather, time):
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

    soil.trans_sum = 0.0
    soil.evap_sum = 0.0
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
        soil.trans_sum += trans
        soil.evap_sum += evap
        soil.ET_act += (evap + trans)

        layer.soil_water = SW

        layer.wfps = SW / layer.sat_water

        soil.soil_layers[x] = layer

    soil.drainage = percolation
    soil.delta_SW = profile_SW - soil.profile_SW
    soil.profile_SW = profile_SW

    R = weather.rainfall[time.year - 1][time.day - 1]

    soil.p_act = R
    soil.p_calc = soil.delta_SW + soil.ET_act + soil.drainage + soil.runoff

    soil.water_balance_difference = soil.p_act - soil.p_calc
