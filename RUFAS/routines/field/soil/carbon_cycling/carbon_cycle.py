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
    d_AG_lignin_res_percent = 0.12 * weather.rainfall[time.year - 1][time.day - 1] * 0.01
    soil.AG_lignin_res_percent += d_AG_lignin_res_percent

    # S.6.A.2
    LN_AG = 0
    crop_type.fr_N = 0.4  # TODO calculate in RuFaS but not "accurate" for carbon use
    if crop_type.fr_N != 0:
        LN_AG = (soil.AG_lignin_res_percent / 100) / crop_type.fr_N

    # S.6.A.3
    AG_met_percent = 0.85 - 0.18 * LN_AG

    soil.LN_AG = LN_AG

    K2 = 0.28
    AG_met_active_decomp = K2

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
        layer.AG_met_to_C_active = AG_met_active_decomp * layer.M_d * soil.T_d * layer.AG_met

        # S.6.A.7
        AG_met_to_BG = layer.AG_met * layer.tillage_percent

        # S.6.A.8
        d_AG_met = soil.residue_harvest * AG_met_percent - (
                (layer.AG_met_to_C_active - AG_met_to_BG) + AG_met_to_BG)
        layer.AG_met += d_AG_met

        # above ground structural residue
        K1 = 0.076

        # S.6.A.9
        AG_struct_decomp = K1 * math.exp(-3) * (1 - AG_met_percent)

        # S.6.A.10
        layer.AG_struct_to_C_active = AG_struct_decomp * layer.M_d * soil.T_d * layer.AG_struct
        layer.AG_struct_to_C_slow = AG_struct_decomp * layer.M_d * soil.T_d * layer.AG_struct

        # S.6.A.11
        AG_struct_to_BG = layer.AG_struct * layer.tillage_percent

        # S.6.A.12
        d_AG_struct = ((soil.residue_harvest * (1 - AG_met_percent)) - AG_struct_to_BG) - \
                          (layer.AG_struct_to_C_active + layer.AG_struct_to_C_slow)
        layer.AG_struct += d_AG_struct

        # below ground metabolic residue and roots
        # S.6.A.13
        residue_incorp = layer.tillage_percent * soil.residue_harvest

        # S.6.A.14
        lignin_res_percent = 0
        if residue_incorp + crop_type.bio_BG != 0:
            lignin_res_percent = residue_incorp / (residue_incorp + crop_type.bio_BG)

        # S.6.A.15
        soil.BG_lignin_res_percent = max(0.0, soil.BG_lignin_res_percent - 0.15
                                         * weather.rainfall[time.year - 1][time.day - 1] * 0.01)

        # S.6.A.16
        LN_BG = 0
        if crop_type.fr_N != 0:
            LN_BG = LN_AG * lignin_res_percent + (((soil.BG_lignin_res_percent / 100) / crop_type.fr_N) / 100) \
                          * (1 - lignin_res_percent)

        # S.6.A.17
        BG_met_percent = 0.85 - 0.18 * LN_BG

        K4 = 0.35
        BG_met_active_decomp = K4

        # S.6.A.18
        layer.BG_met_to_C_active = BG_met_active_decomp * layer.M_d * soil.T_d * layer.BG_met

        # S.6.A.19
        d_BG_met = AG_met_to_BG + (crop_type.bio_BG * BG_met_percent) - layer.BG_met_to_C_active
        layer.BG_met += d_BG_met

        # below ground structural residue and roots
        K3 = 0.094
        BG_struct_decomp = K3

        # S.6.A.20
        layer.BG_struct_to_C_active = BG_struct_decomp * layer.M_d * soil.T_d * layer.BG_struct
        layer.BG_struct_to_C_slow = BG_struct_decomp * layer.M_d * soil.T_d * layer.BG_struct

        # S.6.A.21
        d_BG_struct = (AG_struct_to_BG + crop_type.bio_BG * (1 - BG_met_percent)) - \
                          ((layer.BG_struct_to_C_active + layer.BG_struct_to_C_slow) + AG_struct_to_BG)
        layer.BG_struct += d_BG_struct


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
        percent_CO2_met_to_active = 0.55
        layer.AG_met_to_C_active_loss = layer.AG_met_to_C_active * percent_CO2_met_to_active
        layer.AG_met_to_C_active_act = layer.AG_met_to_C_active * (1 - percent_CO2_met_to_active)

        # above ground structural C
        fr_CO2_struct_to_active = 0.45
        layer.AG_struct_to_C_active_loss = layer.AG_struct_to_C_active * fr_CO2_struct_to_active
        layer.AG_struct_to_C_active_act = layer.AG_struct_to_C_active * (1 - fr_CO2_struct_to_active)

        fr_CO2_struct_to_slow = 0.3
        layer.AG_struct_to_C_slow_loss = layer.AG_struct_to_C_slow * fr_CO2_struct_to_slow
        layer.AG_struct_to_C_slow_act = layer.AG_struct_to_C_slow * (1 - fr_CO2_struct_to_slow)

        # below ground metabolic C
        layer.BG_met_to_C_active_loss = layer.BG_met_to_C_active * percent_CO2_met_to_active
        layer.BG_met_to_C_active_act = layer.BG_met_to_C_active * (1 - percent_CO2_met_to_active)

        # below ground structural C
        layer.BG_struct_to_C_active_loss = layer.BG_struct_to_C_active * fr_CO2_struct_to_active
        layer.BG_struct_to_C_active_act = layer.BG_struct_to_C_active * (1 - fr_CO2_struct_to_active)

        layer.BG_struct_to_C_slow_loss = layer.BG_struct_to_C_slow * fr_CO2_struct_to_slow
        layer.BG_struct_to_C_slow_act = layer.BG_struct_to_C_slow * (1 - fr_CO2_struct_to_slow)

        # partitioning The Active and Slow Carbon Pools (in soil) Decomposition to Alternative Carbon Pools
        # (e.g., Active Carbon Pool to Slow Carbon Pool) or Gas Loss

        K5 = 0.14
        # S.6.B.2
        C_active_decomp = K5 * (1 - 0.75 * soil.silt_to_clay_percent)

        # S.6.B.3
        C_active_decomp = C_active_decomp * layer.M_d * soil.T_d * layer.C_active

        # S.6.B.4
        K6 = 0.0038
        C_slow_decomp = K6 * layer.M_d * soil.T_d * layer.C_slow

        # S.6.B.5
        K7 = 0.00013
        C_passive_decomp = K7 * layer.M_d * soil.T_d * layer.C_passive

        # S.6.B.6
        Es = 0.85 - 0.68 * soil.silt_to_clay_percent

        # S.6.B.7
        layer.C_active_to_slow = C_active_decomp * (1 - Es - 0.004)
        layer.C_active_loss = C_active_decomp * Es

        # S.6.B.8
        layer.C_active_to_passive = C_active_decomp * 0.004

        percent_CO2_to_C_slow_loss = 0.55
        percent_C_slow_to_passive = 0.03

        # S.6.B.9
        layer.C_slow_to_active = C_slow_decomp * (1 - percent_CO2_to_C_slow_loss - percent_C_slow_to_passive)
        layer.C_slow_loss = C_slow_decomp * percent_CO2_to_C_slow_loss
        layer.C_slow_to_passive = C_slow_decomp * percent_C_slow_to_passive

        percent_CO2_to_C_passive_loss = 0.55

        # S.6.B.10
        layer.C_passive_to_active = C_passive_decomp * (1 - percent_CO2_to_C_passive_loss)
        layer.C_passive_loss = C_passive_decomp * percent_CO2_to_C_passive_loss

        # active, slow and lost CO2 pools

        # aggregate active carbon pool flux
        # S.6.B.11
        d_C_active = (layer.AG_met_to_C_active_act + layer.AG_struct_to_C_active_act +
                           layer.BG_met_to_C_active_act + layer.BG_struct_to_C_active_act +
                           layer.C_passive_to_active + layer.C_slow_to_active) - layer.C_active_decomp
        layer.C_active += d_C_active

        # aggregate slow carbon pool flux
        # S.6.B.12
        d_C_slow = (layer.AG_struct_to_C_slow_act + layer.BG_struct_to_C_slow_act +
                         layer.C_active_to_slow) - C_slow_decomp
        layer.C_slow += d_C_slow

        # aggregate passive carbon pool flux
        # S.6.B.13
        d_carbon_passive = (layer.C_slow_to_passive + layer.C_active_to_passive) - C_passive_decomp
        layer.C_passive += d_carbon_passive


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
        C_active_percent = (layer.C_active / soil_mass) * 100
        C_slow_percent = (layer.C_slow / soil_mass) * 100
        C_passive_percent = (layer.C_passive / soil_mass) * 100

        # S.6.C.3
        layer.C_percent = C_active_percent + C_slow_percent + C_passive_percent
        layer.org_C = layer.C_percent

        # total soil carbon
        # S.6.C.4
        layer.C = layer.C_active + layer.C_slow + layer.C_passive
        layer.C_mg = layer.C * 0.001
        layer.C_g = layer.C * 0.1

        # total CO2 Gas Aggregation
        # S.6.C.5
        AG_CO2_loss = layer.AG_met_to_C_active_loss + layer.AG_struct_to_C_active_loss + \
                      layer.AG_struct_to_C_slow_loss
        BG_CO2_loss = layer.BG_met_to_C_active_loss + layer.BG_struct_to_C_active_loss + \
                      layer.BG_struct_to_C_slow_loss

        # S.6.C.6
        layer.C_CO2_loss_decomp = layer.C_active_loss + layer.C_slow_loss + layer.C_passive_loss

        # S.6.C.7
        layer.C_CO2_loss = AG_CO2_loss + BG_CO2_loss + layer.C_CO2_loss_decomp

    soil.curr_layer_depth = 0
