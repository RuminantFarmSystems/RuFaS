"""
RUFAS: Ruminant Farm Systems Model
File name: nitrogen_cycling.py

Description: Implements the nitrogen cycling process of humus mineralization

Author(s): William Donovan, wmdonovan@wisc.edu
"""


def humus_mineralization(soil):
    """
    Definition:
        Humus mineralization is the movement of Nitrogen between the Active and
        Stable organic pools
        "pseudocode_soil" S.4.F

    Args:
        soil:
    """

    for layer in soil.soil_layers:
        active_N = layer.active_N
        stable_N = layer.stable_N
        frac_N = 0.02 #nitrogen bug 

        # "pseudocode_soil" S.4.F.1
        N_trans = 0.00001 * (active_N * ((1 / frac_N) - 1) - stable_N)
        layer.active_N -= N_trans
        layer.stable_N += N_trans

        layer.N_trans = N_trans
