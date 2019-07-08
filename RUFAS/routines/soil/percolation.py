"""
RUFAS: Ruminant Farm Systems Model

File name: percolation.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water percolation on a given day. Currently the only
             function meant to be used outside of this file is the update_all()
              function. The other functions are meant to serve as helper
              functions within this file.

Soil attribute definitions

    Perc = amount of water that percolates to the underlying soil layer (mm H20)

    t = time step (24h)

    TT = travel time for percolation (h)

    Ksat = saturated hydraulic conductivity (mm/h)

Soil values updated by calling update_all():
    soil.listOfSoilLayers.perc
"""
###############################################################################

from math import exp


#
# This function calls all the necessary functions to update information related
# to percolation
#
def update_all(soil):

    calc_daily_percolation(soil)

    if soil.update_SW:
        update_SW(soil)


#
# Calculates daily percolation as a function of the water available for
# percolation (SWperc) in a soil layer.
# "pseudocode_soil" S.2.C.1/2
#
def calc_daily_percolation(soil):
    #
    # The soil water in each layer is dependent on the amount percolated from
    # the layer above. Because there are no layers above the first, prev_perc
    # is initialized at 0 and updated with each pass of the loop.
    #
    for layer in soil.listOfSoilLayers:
        SAT = layer.satWater

        SW = layer.currentSoilWaterMM
        FC = layer.fcWater
        WP = layer.wiltingWater

        SWperc = 0.0
        if SW > FC:
            SWperc = SW - FC

        Ksat = layer.ksat

        # Travel Time for each soil layer
        # "pseudocode_soil" S.2.C.2
        TT = (SAT - FC) / Ksat
        layer.TT = TT

        t = 24

        exp_part = exp((-t) / layer.TT)
        perc = SWperc * (1 - exp_part)
        layer.perc = min(perc, SW - WP)


def update_SW(soil):
    for x in range(len(soil.listOfSoilLayers)):
        layer = soil.listOfSoilLayers[x]
        SW = layer.currentSoilWaterMM
        SAT = layer.satWater
        layer.currentSoilWaterMM -= layer.perc
        if x > 0:
            perc_in = soil.listOfSoilLayers[x - 1].perc
            if perc_in + SW > SAT:
                perc_in = SAT - SW
                soil.listOfSoilLayers[x - 1].currentSoilWaterMM += soil.listOfSoilLayers[x - 1].perc - perc_in
            layer.currentSoilWaterMM += perc_in

    soil.drainage = soil.listOfSoilLayers[-1].perc
