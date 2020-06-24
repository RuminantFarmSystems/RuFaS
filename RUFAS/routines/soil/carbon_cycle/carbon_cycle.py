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
        weather
        time
    """

    # residue from annual crops

    # above ground metabolic residue
    soil.residue_DM = soil.residue * (1 - soil.plant_moisture)

    # residue partitioning
    soil.lignin_residue = 0  # TODO get from database
    # TODO fr_N might need a different calculation in the future
    LN_ratio_AG = 0
    if crop_type.fr_N != 0:
        LN_ratio_AG = (soil.lignin_residue / 100) / crop_type.fr_N
    metabolic_AG_frac = 0.85 - 0.18 * LN_ratio_AG

    K2 = 0.28
    metabolic_AG_active_decomp = K2
    # TODO get from database, using coarse temporarily
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

    metabolic_AG_to_BG = soil.metabolic_AG * soil.fr_tillage  # TODO fr_tillage, percent_incorp?

    d_metabolic_AG = soil.metabolic_AG - ((metabolic_AG_to_C_active - metabolic_AG_to_BG)
                                          + metabolic_AG_to_BG)
    soil.metabolic_AG = soil.residue_DM * metabolic_AG_frac - d_metabolic_AG

    # above ground structural residue
    K1 = 0.076
    struct_AG_decomp = K1 * math.exp(-3) * (1 - metabolic_AG_frac)
    struct_AG_to_C_active = struct_AG_decomp * M_d * T_d * soil.structural_AG
    struct_AG_to_C_slow = struct_AG_decomp * M_d * T_d * soil.structural_AG

    struct_AG_to_BG = soil.structural_AG * soil.fr_tillage

    d_structural_AG = soil.structural_AG - ((struct_AG_to_C_active + struct_AG_to_C_slow - struct_AG_to_BG)
                                            + struct_AG_to_BG)
    soil.structural_AG = (soil.residue_DM * (1 - metabolic_AG_frac)) - d_structural_AG

    # below ground metabolic residue and roots
    residue_DM_incorp = soil.fr_tillage * soil.residue_DM
    fr_lignin_residue_DM = 0
    if residue_DM_incorp + crop_type.bio_BG_DM != 0:
        fr_lignin_residue_DM = residue_DM_incorp / (residue_DM_incorp + crop_type.bio_BG_DM)

    LN_ratio_BG = 0
    if crop_type.fr_N != 0:
        LN_ratio_BG = LN_ratio_AG * fr_lignin_residue_DM + ((soil.lignin_residue / 100) / crop_type.fr_N) \
                      * (1 - fr_lignin_residue_DM) / 100

    metabolic_BG_frac = 0.85 - 0.18 * LN_ratio_BG

    K4 = 0.35
    metabolic_BG_active_decomp = K4
    metabolic_BG_to_C_active = metabolic_BG_active_decomp * M_d * T_d * soil.metabolic_BG

    d_metabolic_BG = soil.metabolic_BG - metabolic_BG_to_C_active

    soil.metabolic_BG = metabolic_AG_to_BG + crop_type.bio_BG_DM * metabolic_BG_frac - d_metabolic_BG

    # below ground structural residue and roots
    K3 = 0.094
    struct_BG_decomp = K3
    struct_BG_to_C_active = struct_BG_decomp * M_d * T_d * soil.structural_BG
    struct_BG_to_C_slow = struct_BG_decomp * M_d * T_d * soil.structural_BG

    d_structural_BG = soil.structural_BG - (struct_BG_to_C_active + struct_BG_to_C_slow) + struct_AG_to_BG

    soil.structural_BG = struct_AG_to_BG + crop_type.bio_BG_DM * (1 - metabolic_BG_frac) - d_structural_BG

    # partitioning active and slow carbon decomposition to carbon pools or gas loss

    # above ground metabolic C
    fr_CO2_met_to_active = 0.55
    soil.metabolic_AG_to_active_loss = metabolic_AG_to_C_active * fr_CO2_met_to_active
    soil.metabolic_AG_to_active_actual = metabolic_AG_to_C_active * (1 - fr_CO2_met_to_active)

    # above ground structural C
    fr_CO2_struct_to_active = 0.45
    soil.struct_AG_to_active_loss = struct_AG_to_C_active * fr_CO2_struct_to_active
    soil.struct_AG_to_active_actual = struct_AG_to_C_active * (1 - fr_CO2_struct_to_active)

    fr_CO2_struct_to_slow = 0.3
    soil.struct_AG_to_slow_loss = struct_AG_to_C_slow * fr_CO2_struct_to_slow
    soil.struct_AG_to_slow_actual = struct_AG_to_C_slow * (1 - fr_CO2_struct_to_slow)

    # below ground metabolic C
    soil.metabolic_BG_to_active_loss = metabolic_BG_to_C_active * fr_CO2_met_to_active
    soil.metabolic_BG_to_active_actual = metabolic_BG_to_C_active * (1 - fr_CO2_met_to_active)

    # below ground structural C
    soil.struct_BG_to_active_loss = struct_BG_to_C_active * fr_CO2_struct_to_active
    soil.struct_BG_to_active_actual = struct_BG_to_C_active * (1 - fr_CO2_struct_to_active)

    soil.struct_BG_to_slow_loss = struct_BG_to_C_slow * fr_CO2_struct_to_slow
    soil.struct_BG_to_slow_actual = struct_BG_to_C_slow * (1 - fr_CO2_struct_to_slow)
