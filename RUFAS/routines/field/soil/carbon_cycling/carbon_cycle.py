"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_cycling.py

Author(s): Jacob Johnson, jacob8399@gmail.com

Description: Carbon Cycle driver class.
"""

import math


def update_all(soil, crop_type, weather, time):
    """
    Description:
        This function calls all the necessary functions to update information related
        to the carbon cycle. The order in which each method is called is significant.

    Args:
        soil: an instance of the Soil class defined in soil.py
        crop_type: an instance of a BaseCrop representing the crop being grown in this field
        weather: an instance of the Weather class defined in classes.py
        time: an instance of the Time class defined in classes.py
    """

    residue_partitioning(crop_type, soil, weather, time)

    pools_and_gas_partitioning(soil)

    soil_carbon_aggregation(soil)


def residue_partitioning(crop_type, soil, weather, time):
    """
    Description:
        This function does the partitioning of the residue from crop yield
        "pseudocode_soil" S.6.A

    Args:
        soil
        crop_type
        weather
        time
    """

    # S.6.A.1
    d_lignin_residue_AG_percent = 0.12 * weather.rainfall[time.year - 1][time.day - 1] * 0.01
    soil.lignin_residue_AG_percent += d_lignin_residue_AG_percent

    # S.6.A.2
    LN_ratio_AG = 0
    crop_type.fr_N = 0.4  # TODO calculate in RuFaS but not "accurate" for carbon use
    if crop_type.fr_N != 0:
        LN_ratio_AG = (soil.lignin_residue_AG_percent / 100) / crop_type.fr_N

    # S.6.A.3
    metabolic_AG_frac = 0.85 - 0.18 * LN_ratio_AG

    soil.LN_ratio_AG = LN_ratio_AG

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

    # S.6.A.4
    T_d = max(0.0, (teff_2 + (teff_3 / math.pi) * math.atan(math.pi * teff_4 * (
            weather.T_avg[time.year - 1][time.day - 1] - teff_1))) / normalizer)

    soil.T_d = T_d

    for layer in soil.soil_layers:
        # S.6.A.5
        base_1 = (layer.water_fac - b) / (a - b)
        base_2 = (layer.water_fac - c) / (a - c)
        M_d = (base_1 ** e1) * (base_2 ** e2)
        layer.M_d = M_d

        # above ground metabolic residue
        # S.6.A.6
        layer.metabolic_AG_to_C_active = metabolic_AG_active_decomp * layer.M_d * soil.T_d * layer.metabolic_AG

        # S.6.A.7
        metabolic_AG_to_BG = layer.metabolic_AG * layer.fr_tillage

        # S.6.A.8
        d_metabolic_AG = soil.residue_harvest * metabolic_AG_frac - (
                (layer.metabolic_AG_to_C_active - metabolic_AG_to_BG) + metabolic_AG_to_BG)
        layer.metabolic_AG += d_metabolic_AG

        # above ground structural residue
        K1 = 0.076

        # S.6.A.9
        struct_AG_decomp = K1 * math.exp(-3) * (1 - metabolic_AG_frac)

        # S.6.A.10
        layer.struct_AG_to_C_active = struct_AG_decomp * layer.M_d * soil.T_d * layer.structural_AG
        layer.struct_AG_to_C_slow = struct_AG_decomp * layer.M_d * soil.T_d * layer.structural_AG

        # S.6.A.11
        struct_AG_to_BG = layer.structural_AG * layer.fr_tillage

        # S.6.A.12
        d_structural_AG = ((soil.residue_harvest * (1 - metabolic_AG_frac)) - struct_AG_to_BG) - \
                          (layer.struct_AG_to_C_active + layer.struct_AG_to_C_slow)
        layer.structural_AG += d_structural_AG

        # below ground metabolic residue and roots
        # S.6.A.13
        residue_incorp = layer.fr_tillage * soil.residue_harvest

        # S.6.A.14
        fr_lignin_residue = 0
        if residue_incorp + crop_type.bio_BG != 0:
            fr_lignin_residue = residue_incorp / (residue_incorp + crop_type.bio_BG)

        # S.6.A.15
        soil.lignin_residue_BG_percent = max(0.0, soil.lignin_residue_BG_percent - 0.15
                                             * weather.rainfall[time.year - 1][time.day - 1] * 0.01)

        # S.6.A.16
        LN_ratio_BG = 0
        if crop_type.fr_N != 0:
            LN_ratio_BG = LN_ratio_AG * fr_lignin_residue + (((soil.lignin_residue_BG_percent / 100) / crop_type.fr_N)/100) \
                          * (1 - fr_lignin_residue)

        # S.6.A.17
        metabolic_BG_frac = 0.85 - 0.18 * LN_ratio_BG

        K4 = 0.35
        metabolic_BG_active_decomp = K4

        # S.6.A.18
        layer.metabolic_BG_to_C_active = metabolic_BG_active_decomp * layer.M_d * soil.T_d * layer.metabolic_BG

        # S.6.A.19
        d_metabolic_BG = metabolic_AG_to_BG + (crop_type.bio_BG * metabolic_BG_frac) - layer.metabolic_BG_to_C_active
        layer.metabolic_BG += d_metabolic_BG

        # below ground structural residue and roots
        K3 = 0.094
        struct_BG_decomp = K3

        # S.6.A.20
        layer.struct_BG_to_C_active = struct_BG_decomp * layer.M_d * soil.T_d * layer.structural_BG
        layer.struct_BG_to_C_slow = struct_BG_decomp * layer.M_d * soil.T_d * layer.structural_BG

        # S.6.A.21
        d_structural_BG = (struct_AG_to_BG + crop_type.bio_BG * (1 - metabolic_BG_frac)) - \
                          ((layer.struct_BG_to_C_active + layer.struct_BG_to_C_slow) + struct_AG_to_BG)
        layer.structural_BG += d_structural_BG


def pools_and_gas_partitioning(soil):
    """
    Description:
        This function does the partitioning of carbon into pools or gas loss

    Args:
        soil
    """

    for layer in soil.soil_layers:
        # Partitioning active and slow carbon decomposition to carbon pools or gas loss
        # S.6.B.1
        # above ground metabolic C
        fr_CO2_met_to_active = 0.55
        layer.metabolic_AG_to_active_loss = layer.metabolic_AG_to_C_active * fr_CO2_met_to_active
        metabolic_AG_to_active_actual = layer.metabolic_AG_to_C_active * (1 - fr_CO2_met_to_active)

        # above ground structural C
        fr_CO2_struct_to_active = 0.45
        layer.struct_AG_to_active_loss = layer.struct_AG_to_C_active * fr_CO2_struct_to_active
        struct_AG_to_active_actual = layer.struct_AG_to_C_active * (1 - fr_CO2_struct_to_active)
        layer.struct_AG_to_active_actual = struct_AG_to_active_actual

        fr_CO2_struct_to_slow = 0.3
        layer.struct_AG_to_slow_loss = layer.struct_AG_to_C_slow * fr_CO2_struct_to_slow
        struct_AG_to_slow_actual = layer.struct_AG_to_C_slow * (1 - fr_CO2_struct_to_slow)
        layer.struct_AG_to_slow_actual = struct_AG_to_slow_actual

        # below ground metabolic C
        layer.metabolic_BG_to_active_loss = layer.metabolic_BG_to_C_active * fr_CO2_met_to_active
        metabolic_BG_to_active_actual = layer.metabolic_BG_to_C_active * (1 - fr_CO2_met_to_active)
        layer.metabolic_BG_to_active_actual = metabolic_BG_to_active_actual

        # below ground structural C
        layer.struct_BG_to_active_loss = layer.struct_BG_to_C_active * fr_CO2_struct_to_active
        struct_BG_to_active_actual = layer.struct_BG_to_C_active * (1 - fr_CO2_struct_to_active)
        layer.struct_BG_to_active_actual = struct_BG_to_active_actual

        layer.struct_BG_to_slow_loss = layer.struct_BG_to_C_slow * fr_CO2_struct_to_slow
        struct_BG_to_slow_actual = layer.struct_BG_to_C_slow * (1 - fr_CO2_struct_to_slow)
        layer.struct_BG_to_slow_actual = struct_BG_to_slow_actual

        # partitioning The Active and Slow Carbon Pools (in soil) Decomposition to Alternative Carbon Pools
        # (e.g., Active Carbon Pool to Slow Carbon Pool) or Gas Loss

        K5 = 0.14
        # S.6.B.2
        active_decomp = K5 * (1 - 0.75 * soil.silt_and_clay_frac)

        # S.6.B.3
        carbon_active_decomp = active_decomp * layer.M_d * soil.T_d * layer.carbon_active

        # S.6.B.4
        K6 = 0.0038
        carbon_slow_decomp = K6 * layer.M_d * soil.T_d * layer.carbon_slow

        # S.6.B.5
        K7 = 0.00013
        carbon_passive_decomp = K7 * layer.M_d * soil.T_d * layer.carbon_passive

        # S.6.B.6
        Es = 0.85 - 0.68 * soil.silt_and_clay_frac

        # S.6.B.7
        active_to_slow = carbon_active_decomp * (1 - Es - 0.004)
        layer.active_to_slow = active_to_slow
        layer.carbon_active_loss = carbon_active_decomp * Es

        # S.6.B.8
        active_to_passive = carbon_active_decomp * 0.004
        layer.active_to_passive = active_to_passive

        fr_CO2_carbon_slow_loss = 0.55
        fr_slow_to_passive = 0.03

        # S.6.B.9
        slow_to_active = carbon_slow_decomp * (1 - fr_CO2_carbon_slow_loss - fr_slow_to_passive)
        layer.slow_to_active = slow_to_active
        layer.carbon_slow_loss = carbon_slow_decomp * fr_CO2_carbon_slow_loss
        slow_to_passive = carbon_slow_decomp * fr_slow_to_passive
        layer.slow_to_passive = slow_to_passive

        fr_CO2_carbon_passive_loss = 0.55

        # S.6.B.10
        passive_to_active = carbon_passive_decomp * (1 - fr_CO2_carbon_passive_loss)
        layer.passive_to_active = passive_to_active
        layer.carbon_passive_loss = carbon_passive_decomp * fr_CO2_carbon_passive_loss

        # active, slow and lost CO2 pools

        # aggregate active carbon pool flux
        # S.6.B.11
        d_carbon_active = (metabolic_AG_to_active_actual + struct_AG_to_active_actual +
                           metabolic_BG_to_active_actual + struct_BG_to_active_actual +
                           passive_to_active + slow_to_active) - carbon_active_decomp
        layer.carbon_active += d_carbon_active

        # aggregate slow carbon pool flux
        # S.6.B.12
        d_carbon_slow = (struct_AG_to_slow_actual + struct_BG_to_slow_actual +
                         active_to_slow) - carbon_slow_decomp
        layer.carbon_slow += d_carbon_slow

        # aggregate passive carbon pool flux
        # S.6.B.13
        d_carbon_passive = (slow_to_passive + active_to_passive) - carbon_passive_decomp
        layer.carbon_passive += d_carbon_passive


def soil_carbon_aggregation(soil):
    """
    Description:
        This function does the aggregation of carbon into pools
        "pseudocode_soil" S.6.C

    Args:
        soil
    """

    for layer in soil.soil_layers:
        # soil mass calculations
        # S.6.C.1
        depth = layer.bottom_depth - soil.curr_layer_depth
        soil.curr_layer_depth += depth

        soil_volume = depth * 10 * soil.area
        soil_mass = (layer.bulk_density / 0.001) * soil_volume

        # aggregate Soil Carbon Pools (Active, Slow, and Passive) and CO2 Gas Flux.

        # carbon pool conversion to percentages and their aggregation (i.e., Total %C)
        # S.6.C.2
        active_C_percent = (layer.carbon_active / soil_mass) * 100
        slow_C_percent = (layer.carbon_slow / soil_mass) * 100
        passive_C_percent = (layer.carbon_passive / soil_mass) * 100

        # S.6.C.3
        layer.carbon_percent = active_C_percent + slow_C_percent + passive_C_percent
        layer.org_C = layer.carbon_percent

        # total soil carbon
        # S.6.C.4
        layer.total_carbon = layer.carbon_active + layer.carbon_slow + layer.carbon_passive
        layer.total_carbon_mg = layer.total_carbon * 0.001
        layer.total_carbon_g = layer.total_carbon * 0.1

        # total CO2 Gas Aggregation
        # S.6.C.5
        CO2_AG_loss = layer.metabolic_AG_to_active_loss + layer.struct_AG_to_active_loss + layer.struct_AG_to_slow_loss
        CO2_BG_loss = layer.metabolic_BG_to_active_loss + layer.struct_BG_to_active_loss + layer.struct_BG_to_slow_loss

        # S.6.C.6
        layer.CO2_C_pool_loss_decomp = layer.carbon_active_loss + layer.carbon_slow_loss + layer.carbon_passive_loss

        # S.6.C.7
        layer.total_CO2_C_loss = CO2_AG_loss + CO2_BG_loss + layer.CO2_C_pool_loss_decomp

    soil.curr_layer_depth = 0
