"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Determines nitrogen transfers from leaching runoff and erosion.
             Part of the Nitrogen Cycling process.
"""

from math import exp, log


#
# Calculates/updates N lost in leaching, runoff, and erosion
# "pseudocode_soil" S.4.C
#
def leaching_runoff_erosion(soil):
    # prev_NO3_perc = 0
    # prev_NH4_perc = 0
    # prev_active_N_perc = 0

    for layer in soil.soil_layers:

        #
        # N in leaching is added to the next deeper layer. These values are
        # calculated as the last step of each iteration through the loop. They
        # are initialized at 0 because there is no nitrogen gained through
        # leaching for the first layer.
        #
        # Toggle these comments to change order
        # of operations + updates.
        #
        # layer.NO3 += prev_NO3_perc
        # layer.NH4 += prev_NH4_perc
        # layer.active_N += prev_active_N_perc

        SW = layer.soil_water
        FC = layer.fc_water
        SAT = layer.sat_water

        BD = layer.bulk_density
        thickness = layer.thickness

        #
        # the coefficient of extraction for leaching is calibrated to 2.5
        # for layers 2 and 3
        #
        Cl = 2.5

        #
        # All N lost in runoff and erosion is removed from layer 1
        #
        if layer.name == "Layer1":

            # "pseudocode_soil" S.4.C.1
            runoff = soil.runoff
            w = runoff + SW

            if w == 0:
                NO3RunoffConc = 0
                NH4RunoffConc = 0

            else:
                exp_part = exp(-w / SAT)
                NO3RunoffConc = layer.NO3 * (1 - exp_part) / w
                NH4RunoffConc = layer.NH4 * (1 - exp_part) / w

            Cr = 0.1

            # "pseudocode_soil" S.4.C.2
            NO3Runoff = NO3RunoffConc * Cr * runoff
            NH4Runoff = NH4RunoffConc * runoff

            # it is important for the order of operations that the pools are
            # updated after each process and that those updated values are used
            # thereafter
            soil.NO3_runoff = min(layer.NO3, NO3Runoff)
            layer.NO3 -= soil.NO3_runoff
            soil.NH4_runoff = min(layer.NH4, NH4Runoff)
            layer.NH4 -= soil.NH4_runoff

            soil.NO3_runoff_annual += soil.NO3_runoff
            soil.NH4_runoff_annual += soil.NH4_runoff

            # "pseudocode_soil" S.4.C.3
            active_N_erosion_conc = (100 * layer.active_N) / (BD * thickness)
            stable_NErosConc = (100 * layer.stable_N) / (BD * thickness)
            fresh_NErosConc = (100 * soil.fresh_N / (BD * thickness))
            NH4ErosConc = (100 * layer.NH4 / (BD * thickness))

            Eros_active_N_loss = 0
            Eros_stable_N_loss = 0
            Eros_fresh_N_loss = 0
            Eros_NH4_loss = 0

            Sed = soil.sed

            if Sed > 0:
                # "pseudocode_soil" S.4.C.5
                ER = exp(1.21 - 0.16 * log(Sed * 1000))

                # "pseudocode_soil" S.4.C.4
                Eros_active_N_loss = 0.001 * active_N_erosion_conc * Sed * ER
                Eros_stable_N_loss = 0.001 * stable_NErosConc * Sed * ER
                Eros_fresh_N_loss = 0.001 * fresh_NErosConc * Sed * ER
                Eros_NH4_loss = 0.001 * NH4ErosConc * Sed * ER

            soil.active_N_erosion = min(layer.active_N, Eros_active_N_loss)
            layer.active_N -= soil.active_N_erosion

            soil.stable_N_erosion = min(layer.stable_N, Eros_stable_N_loss)
            layer.stable_N -= soil.stable_N_erosion

            soil.fresh_N_erosion = min(soil.fresh_N, Eros_fresh_N_loss)
            soil.fresh_N -= soil.fresh_N_erosion

            soil.NH4_erosion = min(layer.NH4, Eros_NH4_loss)
            layer.NH4 -= soil.NH4_erosion

            soil.active_N_erosion_annual += soil.active_N_erosion
            soil.stable_N_erosion_annual += soil.stable_N_erosion
            soil.fresh_N_erosion_annual += soil.fresh_N_erosion
            soil.NH4_erosion_annual += soil.NH4_erosion

            #
            # the coefficient of extraction for leaching is calibrated to 1.0
            # for layer 1
            #
            Cl = 1.0

        # "pseudocode_soil" S.4.C.6-8
        Perc = layer.perc
        NO3Perc = 0
        NH4Perc = 0
        activePerc = 0

        if Perc > 0:
            # "pseudocode_soil" S.4.C.6
            NO3PercConc = layer.NO3 / (FC + Perc)
            NH4PercConc = layer.NH4 / (FC + Perc)

            # "pseudocode_soil" S.4.C.7
            activeConc = layer.active_N / (FC + Perc) / 50

            # "pseudocode_soil" S.4.C.8
            NO3Perc = NO3PercConc * Perc / Cl
            NH4Perc = NH4PercConc * Perc
            activePerc = activeConc * Perc

        #
        # N in leaching is removed from a given soil layer and added to the
        # next deeper layer (note that prev_NO3/NH4/active_N_perc are added to the
        # current pools as the first step of the next iteration through the
        # loop. These values are set to 0 before the loop begins because there
        # is no N gained through leaching in the first layer)
        #

        layer.NO3_perc = min(layer.NO3, NO3Perc)
        layer.NH4_perc = min(layer.NH4, NH4Perc)
        layer.active_N_perc = min(layer.active_N, activePerc)

        # layer.NO3 -= NO3Perc
        # layer.NH4 -= NH4Perc
        # layer.active_N -= activePerc
        #
        # prev_NO3_perc = NO3Perc
        # prev_NH4_perc = NH4Perc
        # prev_active_N_perc = activePerc

    # Updates each pool with calculated leaching information
    for x in range(0, len(soil.soil_layers)):
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

    soil.NO3_drainage_annual += soil.NO3_drainage
    soil.NH4_drainage_annual += soil.NH4_drainage
    soil.active_N_drainage_annual += soil.soil_layers[-1].active_N_perc


