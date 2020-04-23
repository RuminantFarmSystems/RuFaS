"""
RUFAS: Ruminant Farm Systems Model
File name: nitrogen_cycling.py

Description: Implements the nitrogen cycling process of denitrification.

Author(s): William Donovan, wmdonovan@wisc.edu

"""

from math import exp


def denitrification(soil):
    """
    Description:
        Calculates denitrification (the bacterial conversion of NO3 to gas under
        anaerobic conditions).
        "pseudocode_soil" S.4.D
    """

    for layer in soil.soil_layers:
        org_C = layer.org_C
        de_N_rate = layer.de_N_rate
        SW = layer.soil_water
        FC = layer.fc_water

        temp_fac = layer.temp_fac

        # "pseudocode_soil" S.4.D.1
        denitrified_N = 0
        if SW > FC:
            exp_part = exp(-de_N_rate * temp_fac * org_C)
            denitrified_N = layer.NO3 * (1 - exp_part)

        denitrified_N = min(layer.NO3, denitrified_N)
        layer.NO3 -= denitrified_N

        layer.denitrification = denitrified_N
