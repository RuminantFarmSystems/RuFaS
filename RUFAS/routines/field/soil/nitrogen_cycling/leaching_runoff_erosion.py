"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Description: Determines nitrogen transfers from leaching runoff and erosion.
             Part of the Nitrogen Cycling process.

Author(s): William Donovan, wmdonovan@wisc.edu
"""

from math import exp, log


def leaching_runoff_erosion(soil):
    """
    Description:
        Calculates/updates N lost in leaching, runoff, and erosion
        "pseudocode_soil" S.4.C

    Args:
        soil:
    """

    # All N lost in runoff and erosion is removed from layer 1
    layer = soil.soil_layers[0]

    SW = layer.soil_water
    SAT = layer.sat_water

    BD = layer.bulk_density
    thickness = layer.thickness

    # "pseudocode_soil" S.4.C.1
    runoff = soil.runoff
    w = runoff + SW

    if w == 0:
        NO3_runoff_conc = 0
        NH4_runoff_conc = 0

    else:
        exp_part = exp(-w / SAT)
        NO3_runoff_conc = layer.NO3 * (1 - exp_part) / w
        NH4_runoff_conc = layer.NH4 * (1 - exp_part) / w

    Cr = 0.1

    # "pseudocode_soil" S.4.C.2
    NO3_runoff = NO3_runoff_conc * Cr * runoff
    NH4_runoff = NH4_runoff_conc * runoff

    # it is important for the order of operations that the pools are
    # updated after each process and that those updated values are used
    # thereafter
    soil.NO3_runoff = min(layer.NO3, NO3_runoff)
    layer.NO3 -= soil.NO3_runoff
    soil.NH4_runoff = min(layer.NH4, NH4_runoff)
    layer.NH4 -= soil.NH4_runoff

    soil.NO3_runoff_annual += soil.NO3_runoff
    soil.NH4_runoff_annual += soil.NH4_runoff

    # "pseudocode_soil" S.4.C.3
    active_N_eros_conc = (100 * layer.active_N) / (BD * thickness)
    stable_N_eros_conc = (100 * layer.stable_N) / (BD * thickness)
    fresh_N_eros_conc = (100 * layer.top_layer_fresh_N / (BD * thickness))
    NH4_eros_conc = (100 * layer.NH4 / (BD * thickness))

    eros_active_N_loss = 0
    eros_stable_N_loss = 0
    eros_fresh_N_loss = 0
    eros_NH4_loss = 0

    sed = soil.sed

    if sed > 0:
        # "pseudocode_soil" S.4.C.5
        ER = exp(1.21 - 0.16 * log(sed * 1000))

        # "pseudocode_soil" S.4.C.4
        eros_active_N_loss = 0.001 * active_N_eros_conc * sed * ER
        eros_stable_N_loss = 0.001 * stable_N_eros_conc * sed * ER
        eros_fresh_N_loss = 0.001 * fresh_N_eros_conc * sed * ER
        eros_NH4_loss = 0.001 * NH4_eros_conc * sed * ER

    soil.active_N_erosion = min(layer.active_N, eros_active_N_loss)
    layer.active_N -= soil.active_N_erosion

    soil.stable_N_erosion = min(layer.stable_N, eros_stable_N_loss)
    layer.stable_N -= soil.stable_N_erosion

    soil.fresh_N_erosion = min(layer.top_layer_fresh_N, eros_fresh_N_loss)
    layer.top_layer_fresh_N -= soil.fresh_N_erosion

    soil.NH4_erosion = min(layer.NH4, eros_NH4_loss)
    layer.NH4 -= soil.NH4_erosion

    soil.active_N_erosion_annual += soil.active_N_erosion
    soil.stable_N_erosion_annual += soil.stable_N_erosion
    soil.fresh_N_erosion_annual += soil.fresh_N_erosion
    soil.NH4_erosion_annual += soil.NH4_erosion

    # the coefficient of extraction for leaching is calibrated to 1.0
    # for layer 1 only
    layer.Cl = 1.0

    soil.soil_layers[0] = layer

    for layer in soil.soil_layers:

        FC = layer.fc_water

        # "pseudocode_soil" S.4.C.6-8
        percolation = layer.percolation
        NO3_percolation = 0
        NH4_percolation = 0
        active_percolation = 0

        if percolation > 0:
            # "pseudocode_soil" S.4.C.6
            NO3_percolation_conc = layer.NO3 / (FC + percolation)
            NH4_percolation_conc = layer.NH4 / (FC + percolation)

            # "pseudocode_soil" S.4.C.7
            active_conc = layer.active_N / (FC + percolation) / 50

            # "pseudocode_soil" S.4.C.8
            NO3_percolation = NO3_percolation_conc * percolation / layer.Cl
            NH4_percolation = NH4_percolation_conc * percolation
            active_percolation = active_conc * percolation

        layer.NO3_percolation = min(layer.NO3, NO3_percolation)
        layer.NH4_percolation = min(layer.NH4, NH4_percolation)
        layer.active_percolation = min(layer.active_N, active_percolation)

    # Updates each pool with calculated leaching information
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]
        layer.NO3 -= layer.NO3_percolation
        layer.NH4 -= layer.NH4_percolation
        layer.active_N -= layer.active_percolation

        if x != 0:
            prev_layer = soil.soil_layers[x - 1]
            layer.NO3 += prev_layer.NO3_percolation
            layer.NH4 += prev_layer.NH4_percolation
            layer.active_N += prev_layer.active_percolation

    soil.NO3_drainage_annual += soil.soil_layers[-1].NO3_percolation
    soil.NH4_drainage_annual += soil.soil_layers[-1].NH4_percolation
    soil.active_N_drainage_annual += soil.soil_layers[-1].active_percolation
