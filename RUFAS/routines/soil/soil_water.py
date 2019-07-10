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

    trans_act = the amount of water lost to transpiration on a give day (mm H20)
                (this value is taken from the crop module)

Soil values updated by calling update_all():
    soil.SW
    soil.listOfSoilLayers

    Soil Layer attributes updated:
        SW
"""
###############################################################################


#
# This function calls all the necessary functions to update the value of soil
# water
#
def update_all(soil, weather, time):

    if soil.update_SW:
        daily_water_balance(soil, weather, time)
    else:
        update_SW(soil, weather, time)


#
# Calculates soil water by layer
# "pseudocode_soil" S.2.D.1/2
#
def update_SW(soil, weather, time):

    prev_SW = 0
    ET_act = 0
    soil.evap_sum = 0
    soil.trans_sum = 0

    R = weather.rainfall[time.year-1][time.day-1]
    runoff = soil.runoff
    for x in range(0, len(soil.listOfSoilLayers)):
        layer = soil.listOfSoilLayers[x]
        SW = layer.currentSoilWaterMM
        WP = layer.wiltingWater
        SAT = layer.satWater
        perc = layer.perc
        evap = layer.layer_evap
        trans = layer.trans_act
        I = soil.dailyInfiltration

        if x == 0:
            SW = SW + I - evap - perc - trans
            if SW < WP:
                layer.perc -= WP - SW
            SW = max(WP, SW)
            if SW > SAT:
                layer.perc += SW - SAT
            SW = min(SAT, SW)

        else:
            perc_prev = soil.listOfSoilLayers[x-1].perc
            SW = SW + perc_prev - evap - perc - trans
            if SW < WP:
                layer.perc -= WP - SW
            SW = max(WP, SW)
            if SW > SAT:
                layer.perc += SW - SAT
            SW = min(SAT, SW)

        soil.delta_SW += (SW - layer.currentSoilWaterMM)

        layer.currentSoilWaterMM = SW
        soil.listOfSoilLayers[x] = layer

        prev_SW += SW

        ET_act += (evap + trans)
        soil.evap_sum += evap
        soil.trans_sum += trans

    soil.ET_act = ET_act
    soil.prev_SW = prev_SW
    soil.drainage = soil.listOfSoilLayers[-1].perc

    soil.p_act = R
    soil.p_calc = soil.delta_SW + soil.ET_act + runoff + soil.drainage
    soil.water_balance = soil.p_act - soil.p_calc

    soil.drainage_annual += soil.drainage
    soil.runoff_annual += runoff
    soil.p_act_annual += R

    soil.trans_annual += soil.trans_sum
    soil.evap_annual += soil.evap_sum


def daily_water_balance(soil, weather, time):
    R = weather.rainfall[time.year - 1][time.day - 1]
    D = soil.drainage
    runoff = soil.runoff
    soil.evap_sum = 0
    soil.trans_sum = 0
    for layer in soil.listOfSoilLayers:
        soil.evap_sum += layer.layer_evap
        soil.trans_sum += layer.trans_act
    evap = soil.evap_sum
    trans = soil.trans_sum
    SW = sum_SW(soil)
    prev_SW = soil.prev_SW

    d_SW = SW - prev_SW

    soil.p_act = R
    soil.p_calc = d_SW + evap + trans + runoff + D
    soil.water_balance = soil.p_act - soil.p_calc

    # annual values
    soil.drainage_annual += soil.drainage
    soil.runoff_annual += runoff
    soil.p_act_annual += R
    soil.evap_annual += evap
    soil.trans_annual += trans

    soil.prev_SW = SW


def sum_SW(soil):
    SW = 0.0
    for layer in soil.listOfSoilLayers:
        SW += layer.currentSoilWaterMM
    return SW
