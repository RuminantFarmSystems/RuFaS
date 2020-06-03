"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycle.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Implements the nitrogen cycling process of humus mineralization
"""

#
# Nitrogen is allowed to move between the Active and Stable organic pools,
# representing humus mineralization. This method accounts for that process
# "pseudocode_soil" S.4.F
#
def humus_mineralization(soil):
    for layer in soil.soil_layers:
        activeN = layer.activeN
        stableN = layer.stableN
        FracN = 0.02

        # "pseudocode_soil" S.4.F.1
        Ntrans = 0.00001 * (activeN * ((1 / FracN) - 1) - stableN)

        layer.activeN -= Ntrans
        layer.stableN += Ntrans

        layer.nTrans = Ntrans

