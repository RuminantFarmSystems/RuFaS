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
# "pseudocode_SC_soilhydrology.docx" 2.C.1/2
#
def calc_daily_percolation(soil):

    for layer in soil.listOfSoilLayers:
        SW = layer.currentSoilWaterMM
        FC = layer.fcWater


        SWperc = 0.0
        if SW >= FC:
            SWperc = SW - FC

        SAT = layer.saturation
        Ksat = layer.ksat

        depth = layer.depth
        SATwater = SAT * depth

        # Travel Time for each soil layer
        # "pseudocode_SC_soilhydrology.docx" 2.C.2
        TT = (SATwater - FC) / Ksat
        layer.TT = TT

        t = 24

        exp_part = exp((-t) / layer.TT)
        layer.perc = SWperc * (1 - exp_part)

