"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Implements the nitrogen cycling process of denitrification.
"""

from math import exp


#
# Calculates denitrification (the bacterial conversion of NO3 to gas under
# anaerobic conditions).
# "pseudocode_soil" S.4.D
#
def denitrification(soil):
    for layer in soil.listOfSoilLayers:
        OrgC = layer.orgC
        deNrate = 0.1
        SW = layer.currentSoilWaterMM
        FC = layer.fcWater

        tempFac = layer.tempFac

        # "pseudocode_soil" S.4.D.1
        DenitrN = 0
        if SW > FC:
            exp_part = exp(-deNrate * tempFac * OrgC)
            DenitrN = layer.NO3 * (1 - exp_part)

        DenitrN = min(layer.NO3, DenitrN)
        layer.NO3 -= DenitrN

        layer.denitrification = DenitrN
