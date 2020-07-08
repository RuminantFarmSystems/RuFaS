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

    # A. residue from annual crops

    # above ground metabolic residue
    soil.residue_DM = soil.residue * (1 - soil.plant_moisture)

    # B. residue partitioning
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

    teff_1 = 15.400
    teff_2 = 11.750
    teff_3 = 29.700
    teff_4 = 0.03
    normalizer = 20.80546
    T_d = teff_2 + (teff_3 / math.pi) * math.atan(math.pi * teff_4 * (weather.T_avg[time.year - 1][time.day - 1]
                                                                      - teff_1)) / normalizer

    curr_depth = 0

    for layer in soil.soil_layers:
        base_1 = (layer.water_fac - b) / (a - b)
        base_2 = (layer.water_fac - c) / (a - c)
        M_d = (base_1 ** e1) * (base_2 ** e2)

        metabolic_AG_to_C_active = metabolic_AG_active_decomp * M_d * T_d * layer.metabolic_AG

        metabolic_AG_to_BG = layer.metabolic_AG * layer.fr_tillage  # TODO fr_tillage, percent_incorp?

        d_metabolic_AG = soil.residue_DM * metabolic_AG_frac - (
                (metabolic_AG_to_C_active - metabolic_AG_to_BG) + metabolic_AG_to_BG)

        layer.metabolic_AG += d_metabolic_AG

        # above ground structural residue
        K1 = 0.076
        struct_AG_decomp = K1 * math.exp(-3) * (1 - metabolic_AG_frac)

        struct_AG_to_C_active = struct_AG_decomp * M_d * T_d * layer.structural_AG
        struct_AG_to_C_slow = struct_AG_decomp * M_d * T_d * layer.structural_AG

        struct_AG_to_BG = layer.structural_AG * layer.fr_tillage

        d_structural_AG = (soil.residue_DM * (1 - metabolic_AG_frac)) - \
                          ((struct_AG_to_C_active + struct_AG_to_C_slow - struct_AG_to_BG) + struct_AG_to_BG)

        layer.structural_AG += d_structural_AG

        # below ground metabolic residue and roots
        residue_DM_incorp = layer.fr_tillage * soil.residue_DM
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
        metabolic_BG_to_C_active = metabolic_BG_active_decomp * M_d * T_d * layer.metabolic_BG

        d_metabolic_BG = metabolic_AG_to_BG + crop_type.bio_BG_DM * metabolic_BG_frac - metabolic_BG_to_C_active

        layer.metabolic_BG += d_metabolic_BG

        # below ground structural residue and roots
        K3 = 0.094
        struct_BG_decomp = K3
        struct_BG_to_C_active = struct_BG_decomp * M_d * T_d * layer.structural_BG
        struct_BG_to_C_slow = struct_BG_decomp * M_d * T_d * layer.structural_BG

        d_structural_BG = (struct_AG_to_BG + crop_type.bio_BG_DM * (1 - metabolic_BG_frac)) - (
                struct_BG_to_C_active + struct_BG_to_C_slow) + struct_AG_to_BG

        layer.structural_BG += d_structural_BG

        # C. partitioning active and slow carbon decomposition to carbon pools or gas loss

        # above ground metabolic C
        fr_CO2_met_to_active = 0.55
        layer.metabolic_AG_to_active_loss = metabolic_AG_to_C_active * fr_CO2_met_to_active
        layer.metabolic_AG_to_active_actual = metabolic_AG_to_C_active * (1 - fr_CO2_met_to_active)

        # above ground structural C
        fr_CO2_struct_to_active = 0.45
        layer.struct_AG_to_active_loss = struct_AG_to_C_active * fr_CO2_struct_to_active
        layer.struct_AG_to_active_actual = struct_AG_to_C_active * (1 - fr_CO2_struct_to_active)

        fr_CO2_struct_to_slow = 0.3
        layer.struct_AG_to_slow_loss = struct_AG_to_C_slow * fr_CO2_struct_to_slow
        layer.struct_AG_to_slow_actual = struct_AG_to_C_slow * (1 - fr_CO2_struct_to_slow)

        # below ground metabolic C
        layer.metabolic_BG_to_active_loss = metabolic_BG_to_C_active * fr_CO2_met_to_active
        layer.metabolic_BG_to_active_actual = metabolic_BG_to_C_active * (1 - fr_CO2_met_to_active)

        # below ground structural C
        layer.struct_BG_to_active_loss = struct_BG_to_C_active * fr_CO2_struct_to_active
        layer.struct_BG_to_active_actual = struct_BG_to_C_active * (1 - fr_CO2_struct_to_active)

        layer.struct_BG_to_slow_loss = struct_BG_to_C_slow * fr_CO2_struct_to_slow
        layer.struct_BG_to_slow_actual = struct_BG_to_C_slow * (1 - fr_CO2_struct_to_slow)

        # D. active, slow and lost CO2 pools

        # inputs to the active carbon pool
        K5 = 0.14
        active_decomp = K5 * (1 - 0.75 * soil.silt_and_clay_frac)
        carbon_active_decomp = active_decomp * M_d * T_d * layer.carbon_active

        d_carbon_active = (layer.metabolic_AG_to_active_actual + layer.struct_AG_to_active_actual +
                           layer.metabolic_BG_to_active_actual + layer.struct_BG_to_active_actual +
                           layer.passive_to_active + layer.slow_to_active) - carbon_active_decomp
        layer.carbon_active += d_carbon_active

        # inputs to the slow carbon pool
        K6 = 0.0038
        carbon_slow_decomp = K6 * M_d * T_d * layer.carbon_slow

        d_carbon_slow = (layer.struct_AG_to_slow_actual + layer.struct_BG_to_slow_actual +
                         layer.active_to_slow) - carbon_slow_decomp
        layer.carbon_slow += d_carbon_slow

        # inputs to the passive carbon pool
        K7 = 0.00013
        carbon_passive_decomp = K7 * M_d * T_d * layer.carbon_passive

        d_carbon_passive = (layer.slow_to_passive + layer.active_to_passive) - carbon_passive_decomp
        layer.carbon_passive += d_carbon_passive

        # E. partitioning The Active  and Slow Carbon Pools (in soil) Decomposition to Alternative Carbon Pools
        # (e.g., Active Carbon Pool to Slow Carbon Pool) or Gas Loss

        Es = 0.85 - 0.68 * soil.silt_and_clay_frac

        layer.active_to_slow = carbon_active_decomp * (1 - Es - 0.004)
        carbon_active_loss = carbon_active_decomp * Es

        layer.active_to_passive = carbon_active_decomp * 0.004

        fr_CO2_carbon_slow_loss = 0.55
        fr_slow_to_passive = 0.03

        layer.slow_to_active = carbon_slow_decomp * (1 - fr_CO2_carbon_slow_loss - fr_slow_to_passive)
        carbon_slow_loss = carbon_slow_decomp * (1 - fr_CO2_carbon_slow_loss)
        layer.slow_to_passive = carbon_slow_decomp * fr_slow_to_passive

        fr_CO2_carbon_passive_loss = 0.55

        layer.passive_to_active = carbon_passive_decomp * (1 - fr_CO2_carbon_passive_loss)
        carbon_passive_loss = carbon_passive_decomp * fr_CO2_carbon_passive_loss

        # F. soil mass calculations

        if layer.name == "Layer1":
            depth = layer.bottom_depth

        else:
            depth = layer.bottom_depth - curr_depth
        curr_depth += depth

        soil_volume = depth / 10 * soil.area
        soil_mass = (layer.bulk_density / 0.001) * soil_volume

        # G. aggregate Soil Carbon Pools (Active, Slow, and Passive) and CO2 Gas Flux.

        # carbon pool conversion to percentages and their aggregation (i.e., Total %C)
        active_C_percent = layer.carbon_active / soil_mass
        slow_C_percent = layer.carbon_slow / soil_mass
        passive_C_percent = layer.carbon_passive / soil_mass

        layer.carbon_percent = active_C_percent + slow_C_percent + passive_C_percent

        # total soil carbon
        layer.total_carbon = layer.carbon_active + layer.carbon_slow + layer.carbon_passive
        layer.total_carbon_mg = layer.total_carbon * 0.001
        layer.total_carbon_g = layer.total_carbon * 0.1

        # total CO2 Gas Aggregation
        CO2_AG_loss = layer.metabolic_AG_to_active_loss + layer.struct_AG_to_active_loss + layer.struct_AG_to_slow_loss
        CO2_BG_loss = layer.metabolic_BG_to_active_loss + layer.struct_BG_to_active_loss + layer.struct_BG_to_slow_loss
        CO2_C_pool_decomp_loss = carbon_active_loss + carbon_slow_loss + carbon_passive_loss

        layer.total_CO2_C_loss = CO2_AG_loss + CO2_BG_loss + CO2_C_pool_decomp_loss










