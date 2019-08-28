"""
RUFAS: Ruminant Farm Systems Model

File name: percolation.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water percolation on a given day. Currently the only
             function meant to be used outside of this file is the update_all()
             function. The other functions are meant to serve as helper
             methods within this file.

Soil attribute definitions

    perc = amount of water that percolates to the underlying soil layer (mm H20)

    t = time step (24h)

    TT = travel time for percolation (h)

    Ksat = saturated hydraulic conductivity (mm/h)

Soil values updated by calling update_all():
    soil.soil_layers.perc
"""
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
# "pseudocode_soil" S.2.C.1/2
#
def calc_daily_percolation(soil):
    for layer in soil.soil_layers:
        SAT = layer.sat_water

        SW = layer.soil_water
        FC = layer.fc_water
        WP = layer.wilting_water

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
        layer.perc = min(SW - WP, perc)
