###############################################################################
'''
RUFAS: Ruminant Farm Systems Model

File name: infiltration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating the soil water in the profile at the end of a given day.
             Currently the only function meant to be used outside of this file
             is the update_all() function. The other functions are meant to
             serve as helper functions within this file.

Soil attribute definitions

    Q = daily runoff (mm H20)

    R = daily rainfall depth (mm H20)

    SW = soil water content of entire profile (mm H20)

    FC = amount of water in soil profile at field capacity (mm H20)

    WP = amount of water in the soil profile held at wilting point (mm H20)

    Perc = the amount of water percolated to the next layer (mm H20)

    Et_actual = the amount of water lost to transpiration on a give day (mm H20)
                (this value is taken from the crop module)

Soil values updated by calling update_all():
    soil.SW
    soil.listOfSoilLayers

    Soil Layer attributes updated:
        SW
'''
###############################################################################


#
# This function calls all the necessary functions to update the value of soil
# water
#
def update_all(soil, weather, time):

    update_SW(soil, weather, time)


#
# Calculates soil water by layer
# "pseudocode_SC_soilhydrology.docx" 2.D.1/2
#
def update_SW(soil, weather, time):

    R = weather.rainfall[time.year-1][time.day-1]
    Q = soil.runoff
    for x in range(0, len(soil.listOfSoilLayers)):
        layer = soil.listOfSoilLayers[x]
        SW = layer.currentSoilWaterMM
        WP = layer.wiltingWater
        Perc = layer.perc
        Esoil = layer.layerEsoil

        Et_actual = layer.Et_actual

        if x == 0:
            SW = max(WP, SW + R - Q - Esoil - Perc - Et_actual)

        else:
            Perc_prev = soil.listOfSoilLayers[x-1].perc

            SW = max(WP, SW + Perc_prev - Esoil - Perc - Et_actual)

        layer.currentSoilWaterMM = SW
        soil.listOfSoilLayers[x] = layer
