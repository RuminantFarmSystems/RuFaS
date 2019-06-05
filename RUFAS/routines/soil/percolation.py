'''
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
'''
###############################################################################

from math import exp


#
# This function calls all the necessary functions to update information related
# to percolation
#
def update_all(soil):

    calc_daily_percolation(soil)


#
# Calculates daily percolation as a function of the water available for
# percolation (SWperc) in a soil layer.
# "pseudocode_soil" 2.C.1/2
#
def calc_daily_percolation(soil):
    #
    # The soil water in each layer is dependent on the amount percolated from
    # the layer above. Because there are no layers above the first, prev_perc
    # is initialized at 0 and updated with each pass of the loop.
    #
    prev_perc = 0
    for layer in soil.listOfSoilLayers:
        WP = layer.wiltingWater
        SAT = layer.satWater

        layer.currentSoilWaterMM = min(SAT, layer.currentSoilWaterMM + prev_perc)
        SW = layer.currentSoilWaterMM
        FC = layer.fcWater

        SWperc = 0.0
        if SW > FC:
            SWperc = SW - FC

        Ksat = layer.ksat

        # Travel Time for each soil layer
        # "pseudocode_soil" 2.C.2
        TT = (SAT - FC) / Ksat
        layer.TT = TT

        t = 24

        exp_part = exp((-t) / layer.TT)
        layer.perc = SWperc * (1 - exp_part)
        layer.currentSoilWaterMM = max(WP, SW - layer.perc)
        prev_perc = layer.perc

