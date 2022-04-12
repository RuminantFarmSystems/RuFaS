import math

def update_all(soil, crop_type, weather, time):
    """
    Description:
        Partitions residue from crop yield
        "pseudocode_soil" S.6.B

    Args:
        soil: an instance of the Soil class defined in soil.py
        crop_type: the instance of BaseCrop stored in crop.current_crop
        weather: an instance of the Weather class defined in classes.py
        time: an instance of the Time class defined in time.py
    """

    residue_partitioning(soil, crop_type, weather, time)


def residue_partitioning(soil, crop_type, weather, time):
    """
    Description:
        Partitions residue from crop yield
        "pseudocode_soil" S.6.B

    Args:
        soil
        crop_type
        weather
        time
    """

    # Above ground lignin, metabolic C, and structural C
    # S.6.B.I

    # S.6.B.I.1
    soil.AG_lignin_res_percent += 0.12 * weather.rainfall[time.year - 1][time.day - 1] * 0.01

    # S.6.B.I.2
    AG_L_to_N = 0
    fr_N = 0.4  # TODO calculate in RuFaS [C.5.B.1] but not "accurate" for carbon use
    if fr_N != 0:
        AG_L_to_N = (soil.AG_lignin_res_percent / 100) / fr_N

    # S.6.B.I.3
    AG_met_percent = 0.85 - 0.18 * AG_L_to_N

    soil.AG_L_to_N = AG_L_to_N

    K2 = 0.04
    AG_met_active_decomp = K2

    # above ground structural residue
    K1 = 0.010857
    # S.6.B.I.9
    AG_struct_decomp = K1 * math.exp(-3) * (1 - AG_met_percent)

    for layer_number, layer in enumerate(soil.soil_layers):
        # above ground metabolic residue
        # S.6.B.I.5
        layer.AG_met_to_C_active = AG_met_active_decomp * layer.M_d * soil.T_d * layer.AG_met

        # S.6.B.I.6
        AG_met_to_BG_met = layer.AG_met * layer.tillage_percent

        # S.6.B.I.4 / S.6.B.I.7
       
        if layer_number == 0: #for top layer

            # S.6.B.I.11
            residue_incorp = layer.tillage_percent * soil.residue_harvest

            AG_struct_to_BG_struct = layer.AG_struct * layer.tillage_percent

            if crop_type.extracted == True: #if we extract biomass
                
                ag_biomass = soil.residue_harvest

            else: #if we incorporate biomass
                ag_biomass = crop_type.bio_AG

        else: #non top layers
            
            AG_struct_to_BG_struct = 0

            residue_incorp = 0

            ag_biomass = 0

        # S.6.B.I.4 / S.6.B.I.7
        layer.AG_met += ag_biomass * AG_met_percent - (
            (layer.AG_met_to_C_active - AG_met_to_BG_met) + AG_met_to_BG_met)

        layer.AG_struct += ((ag_biomass * (1 - AG_met_percent)) - AG_struct_to_BG_struct) - \
                        (layer.AG_struct_to_C_active + layer.AG_struct_to_C_slow)

        # S.6.B.I.10
        layer.AG_struct_to_C_active = AG_struct_decomp * layer.M_d * soil.T_d * layer.AG_struct
        
        layer.AG_struct_to_C_slow = AG_struct_decomp * layer.M_d * soil.T_d * layer.AG_struct


        # below ground metabolic residue and roots
        # S.6.B.II

        # S.6.B.II.2
        lignin_res_percent = 0
        if residue_incorp + crop_type.bio_BG != 0:
            lignin_res_percent = residue_incorp / (residue_incorp + crop_type.bio_BG)

        # S.6.B.II.3
        soil.BG_lignin_res_percent = max(0.0, soil.BG_lignin_res_percent - 0.15
                                         * weather.rainfall[time.year - 1][time.day - 1] * 0.01)

        # S.6.B.II.4
        BG_L_to_N = 0
        if crop_type.fr_N != 0:
            BG_L_to_N = AG_L_to_N * lignin_res_percent + (((soil.BG_lignin_res_percent / 100) / crop_type.fr_N) / 100) \
                          * (1 - lignin_res_percent)

        # S.6.B.II.5
        BG_met_percent = 0.85 - 0.18 * BG_L_to_N

        K4 = 0.05

        BG_met_active_decomp = K4

        # S.6.B.II.7
        layer.BG_met_to_C_active = BG_met_active_decomp * layer.M_d * soil.T_d * layer.BG_met

        ADJ_crop_type_bio_BG = (layer.thickness / soil.profile_depth) * crop_type.bio_BG

        # S.6.B.II.6 / S.6.B.II.8
        layer.BG_met += AG_met_to_BG_met + (ADJ_crop_type_bio_BG * BG_met_percent) - layer.BG_met_to_C_active

        # below ground structural residue and roots
        K3 = 0.0134

        BG_struct_decomp = K3

        # S.6.B.II.10
        layer.BG_struct_to_C_active = BG_struct_decomp * layer.M_d * soil.T_d * layer.BG_struct
        layer.BG_struct_to_C_slow = BG_struct_decomp * layer.M_d * soil.T_d * layer.BG_struct

        # S.6.B.II.9 / S.6.B.II.11
        layer.BG_struct += (AG_struct_to_BG_struct + crop_type.bio_BG * (1 - BG_met_percent)) - \
                          ((layer.BG_struct_to_C_active + layer.BG_struct_to_C_slow) + AG_struct_to_BG_struct)
