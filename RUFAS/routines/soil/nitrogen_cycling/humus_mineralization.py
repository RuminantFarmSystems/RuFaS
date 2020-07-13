"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

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
        active_N = layer.active_N
        stable_N = layer.stable_N
        FracN = 0.02

        # "pseudocode_soil" S.4.F.1
        Ntrans = 0.00001 * (active_N * ((1 / FracN) - 1) - stable_N)

        layer.active_N -= Ntrans
        layer.stable_N += Ntrans

        layer.nTrans = Ntrans

