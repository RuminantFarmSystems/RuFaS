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
    # prev_active_perc = 0

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
        # layer.activeN += prev_active_perc

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
            NO3Runoff = min(layer.NO3, NO3Runoff)
            layer.NO3 -= NO3Runoff
            NH4Runoff = min(layer.NH4, NH4Runoff)
            layer.NH4 -= NH4Runoff

            # "pseudocode_soil" S.4.C.3
            activeNErosConc = (100 * layer.activeN) / (BD * thickness)
            stableNErosConc = (100 * layer.stableN) / (BD * thickness)
            freshNErosConc = (100 * layer.topLayerFreshN / (BD * thickness))
            NH4ErosConc = (100 * layer.NH4 / (BD * thickness))

            Eros_activeN_loss = 0
            Eros_stableN_loss = 0
            Eros_freshN_loss = 0
            Eros_NH4_loss = 0

            Sed = soil.sedimentYield

            if Sed > 0:
                # "pseudocode_soil" S.4.C.5
                ER = exp(1.21 - 0.16 * log(Sed * 1000))

                # "pseudocode_soil" S.4.C.4
                Eros_activeN_loss = 0.001 * activeNErosConc * Sed * ER
                Eros_stableN_loss = 0.001 * stableNErosConc * Sed * ER
                Eros_freshN_loss = 0.001 * freshNErosConc * Sed * ER
                Eros_NH4_loss = 0.001 * NH4ErosConc * Sed * ER

            Eros_activeN_loss = min(layer.activeN, Eros_activeN_loss)
            layer.activeN -= Eros_activeN_loss

            Eros_stableN_loss = min(layer.stableN, Eros_stableN_loss)
            layer.stableN -= Eros_stableN_loss

            Eros_freshN_loss = min(layer.topLayerFreshN, Eros_freshN_loss)
            layer.topLayerFreshN -= Eros_freshN_loss

            Eros_NH4_loss = min(layer.NH4, Eros_NH4_loss)
            layer.NH4 -= Eros_NH4_loss

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
            activeConc = layer.activeN / (FC + Perc) / 50

            # "pseudocode_soil" S.4.C.8
            NO3Perc = NO3PercConc * Perc / Cl
            NH4Perc = NH4PercConc * Perc
            activePerc = activeConc * Perc

        #
        # N in leaching is removed from a given soil layer and added to the
        # next deeper layer (note that prev_NO3/NH4/active_perc are added to the
        # current pools as the first step of the next iteration through the
        # loop. These values are set to 0 before the loop begins because there
        # is no N gained through leaching in the first layer)
        #

        layer.NO3Perc = min(layer.NO3, NO3Perc)
        layer.NH4Perc = min(layer.NH4, NH4Perc)
        layer.activePerc = min(layer.activeN, activePerc)

        # layer.NO3 -= NO3Perc
        # layer.NH4 -= NH4Perc
        # layer.activeN -= activePerc
        #
        # prev_NO3_perc = NO3Perc
        # prev_NH4_perc = NH4Perc
        # prev_active_perc = activePerc

    # Updates each pool with calculated leaching information
    for x in range(0, len(soil.soil_layers)):
        layer = soil.soil_layers[x]
        layer.NO3 -= layer.NO3Perc
        layer.NH4 -= layer.NH4Perc
        layer.activeN -= layer.activePerc

        if x != 0:
            prev_layer = soil.soil_layers[x - 1]
            layer.NO3 += prev_layer.NO3Perc
            layer.NH4 += prev_layer.NH4Perc
            layer.activeN += prev_layer.activePerc


