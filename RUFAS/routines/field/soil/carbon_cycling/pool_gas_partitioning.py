def update_all(soil):
    """
    Description:
        This function does the partitioning of carbon into pools or gas loss
        "pseudocode_soil" S.6.C

    Args:
        soil: an instance of the Soil class defined in soil.py
    """

    for layer in soil.soil_layers:
        # Partitioning active and slow carbon decomposition to carbon pools or gas loss
        # S.6.C.1
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
        # S.6.C.2
        C_active_decomp_rate = K5 * (1 - 0.75 * soil.silt_to_clay_percent)

        # S.6.C.3
        layer.C_active_decomp = C_active_decomp_rate * layer.M_d * soil.T_d * layer.C_active

        # S.6.C.4
        K6 = 0.0038
        layer.C_slow_decomp = K6 * layer.M_d * soil.T_d * layer.C_slow

        # S.6.C.5
        K7 = 0.00013
        layer.C_passive_decomp = K7 * layer.M_d * soil.T_d * layer.C_passive

        # S.6.B.6
        Es = 0.85 - 0.68 * soil.silt_to_clay_percent

        # S.6.C.7
        layer.C_active_to_slow = layer.C_active_decomp * (1 - Es - 0.004)
        layer.C_active_loss = layer.C_active_decomp * Es

        # S.6.C.8
        layer.C_active_to_passive = layer.C_active_decomp * 0.004

        percent_CO2_to_C_slow_loss = 0.55
        percent_C_slow_to_passive = 0.03

        # S.6.C.9
        layer.C_slow_to_active = layer.C_slow_decomp * (1 - percent_CO2_to_C_slow_loss - percent_C_slow_to_passive)
        layer.C_slow_loss = layer.C_slow_decomp * percent_CO2_to_C_slow_loss
        layer.C_slow_to_passive = layer.C_slow_decomp * percent_C_slow_to_passive

        percent_CO2_to_C_passive_loss = 0.55

        # S.6.C.10
        layer.C_passive_to_active = layer.C_passive_decomp * (1 - percent_CO2_to_C_passive_loss)
        layer.C_passive_loss = layer.C_passive_decomp * percent_CO2_to_C_passive_loss

        # active, slow and lost CO2 pools

        # aggregate active carbon pool flux
        # S.6.C.11
        layer.C_active += (layer.AG_met_to_C_active_act + layer.AG_struct_to_C_active_act +
                           layer.BG_met_to_C_active_act + layer.BG_struct_to_C_active_act +
                           layer.C_passive_to_active + layer.C_slow_to_active) - layer.C_active_decomp

        # aggregate slow carbon pool flux
        # S.6.C.12
        layer.C_slow += (layer.AG_struct_to_C_slow_act + layer.BG_struct_to_C_slow_act +
                         layer.C_active_to_slow) - layer.C_slow_decomp

        # aggregate passive carbon pool flux
        # S.6.C.13
        layer.C_passive += (layer.C_slow_to_passive + layer.C_active_to_passive) - layer.C_passive_decomp
