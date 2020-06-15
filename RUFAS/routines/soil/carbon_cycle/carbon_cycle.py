"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_cycle.py

Author(s): William Donovan, wmdonovan@wisc.edu,
           Jacob Johnson, jacob8399@gmail.com

Description: Carbon Cycle driver class.
"""

import math


def update_all(crop_type, soil, weather, time):
    """
    Description:
        This function calls all the necessary functions to update information related
        to the carbon cycle. The order in which each method is called is significant.

    Args:
        soil
        crop_type
    """

    # residue from annual crops
    soil.plant_moisture = 0.15  # TODO temporary value from Hector
    soil.residue_DM = soil.residue * (1 - soil.plant_moisture)

    # residue partitioning
    soil.lignin_residue = 0  # TODO get from database
    # TODO fr_N might need a different calculation in the future
    soil.LN_ratio_AG = 0
    if crop_type.fr_N != 0:
        soil.LN_ratio_AG = (soil.lignin_residue / 100) / crop_type.fr_N
    metabolic_AG_frac = 0.85 - 0.18 * soil.LN_ratio_AG

    K2 = 0.28
    metabolic_AG_active_decomp = K2
    # TODO get from database, using course temporarily
    a = 0.55
    b = 1.7
    c = -0.007
    e1 = 6.648115
    e2 = 3.22

    base_1 = (soil.soil_layers[0].wfps - b) / (a - b)
    base_2 = (soil.soil_layers[0].wfps - c) / (a - c)
    M_d = (base_1 ** e1) * (base_2 ** e2)

    teff_1 = 15.400
    teff_2 = 11.750
    teff_3 = 29.700
    teff_4 = 0.03
    normalizer = 20.80546
    T_d = teff_2 + (teff_3 / math.pi) * math.atan(math.pi * teff_4 * (weather.T_avg[time.year - 1][time.day - 1]
                                                                      - teff_1)) / normalizer

    metabolic_AG_to_C_active = metabolic_AG_active_decomp * M_d * T_d * soil.metabolic_AG

    metabolic_AG_to_BG = soil.metabolic_AG * soil.fr_tillage  # TODO fr_tillage

    d_metabolic_AG = soil.metabolic_AG - ((metabolic_AG_to_C_active - metabolic_AG_to_BG)
                                          + metabolic_AG_to_BG)
    soil.metabolic_AG = soil.residue_DM * metabolic_AG_frac - d_metabolic_AG

    # above ground structural residue
