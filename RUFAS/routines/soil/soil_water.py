###############################################################################
"""
RUFAS: Ruminant Farm Systems Model

File name: infiltration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil water in the profile at the end of a given day.
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

Soil attribute definitions

    runoff = daily runoff (mm H20)

    R = daily rainfall depth (mm H20)

    SW = soil water content of entire profile (mm H20)

    FC = amount of water in soil profile at field capacity (mm H20)

    WP = amount of water in the soil profile held at wilting point (mm H20)

    perc = the amount of water percolated to the next layer (mm H20)

    trans_act = the amount of water lost to transpiration on a given day (mm H20)
                (this value is taken from the crop module)

Soil values updated by calling update_all():
    soil.SW
    soil.soil_layers

    Soil Layer attributes updated:
        SW
"""
###############################################################################


#
# This function calls all the necessary functions to update the value of soil
# water
#
def update_all(soil, weather, time):

    update_SW(soil, weather, time)


def update_SW(soil, weather, time):

    soil.trans_sum = 0.0
    soil.evap_sum = 0.0
    soil.ET_act = 0.0

    profile_SW = 0
    perc = 0
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]

        SW = layer.soil_water
        WP = layer.wiltingWater
        SAT = layer.satWater

        perc = layer.perc
        evap = layer.evap
        trans = layer.trans_act
        I = soil.infiltration

        if x == 0:
            perc_in = I
        else:
            perc_in = soil.soil_layers[x - 1].perc

        SW = SW + perc_in - evap - perc - trans

        if SW < WP:
            layer.perc -= WP - SW
        SW = max(WP, SW)
        if SW > SAT:
            layer.perc += SW - SAT
        SW = min(SAT, SW)

        profile_SW += SW
        soil.trans_sum += trans
        soil.evap_sum += evap
        soil.ET_act += (evap + trans)

        layer.soil_water = SW
        soil.soil_layers[x] = layer

    soil.drainage = perc
    soil.delta_SW = profile_SW - soil.profile_SW
    soil.profile_SW = profile_SW

    R = weather.rainfall[time.year - 1][time.day - 1]

    soil.p_act = R
    soil.p_calc = soil.delta_SW + soil.ET_act + soil.drainage + soil.runoff

    soil.water_balance_difference = soil.p_act - soil.p_calc

