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

    # "pseudocode_soil" S.4.C.3
    active_N_eros_conc = (100 * layer.active_N) / (BD * thickness)
    stable_N_eros_conc = (100 * layer.stable_N) / (BD * thickness)
    fresh_N_eros_conc = (100 * soil.fresh_N / (BD * thickness))
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

    soil.fresh_N_erosion = min(soil.fresh_N, eros_fresh_N_loss)
    soil.fresh_N -= soil.fresh_N_erosion

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
        perc = layer.perc
        NO3_perc = 0
        NH4_perc = 0
        active_N_perc = 0

        if perc > 0:
            # "pseudocode_soil" S.4.C.6
            NO3_perc_conc = layer.NO3 / (FC + perc)
            NH4_perc_conc = layer.NH4 / (FC + perc)

            # "pseudocode_soil" S.4.C.7
            active_conc = layer.active_N / (FC + perc) / 50

            # "pseudocode_soil" S.4.C.8
            NO3_perc = NO3_perc_conc * perc / layer.Cl
            NH4_perc = NH4_perc_conc * perc
            active_N_perc = active_conc * perc

        layer.NO3_perc = min(layer.NO3, NO3_perc)
        layer.NH4_perc = min(layer.NH4, NH4_perc)
        layer.active_N_perc = min(layer.active_N, active_N_perc)

    # Updates each pool with calculated leaching information
    for x in range(len(soil.soil_layers)):
        layer = soil.soil_layers[x]
        layer.NO3 -= layer.NO3_perc
        layer.NH4 -= layer.NH4_perc
        layer.active_N -= layer.active_N_perc

        if x != 0:
            prev_layer = soil.soil_layers[x - 1]
            layer.NO3 += prev_layer.NO3_perc
            layer.NH4 += prev_layer.NH4_perc
            layer.active_N += prev_layer.active_N_perc

    soil.NO3_drainage = soil.soil_layers[-1].NO3_perc
    soil.NH4_drainage = soil.soil_layers[-1].NH4_perc
    soil.active_N_drainage = soil.soil_layers[-1].active_N_perc
