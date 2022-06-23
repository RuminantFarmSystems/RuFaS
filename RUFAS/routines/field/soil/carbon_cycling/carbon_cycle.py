"""
RUFAS: Ruminant Farm Systems Model

File name: carbon_cycling.py

Author(s): Jacob Johnson, jacob8399@gmail.com

Description: Carbon Cycle driver class.
"""

from . import decomp_factors, pool_gas_partitioning, residue_partitioning


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

    decomp_factors.update_all(soil, weather, time)

    residue_partitioning.update_all(soil, crop_type, weather, time)

    pool_gas_partitioning.update_all(soil)

    soil_carbon_aggregation(soil)


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
        # S.6.D.1
        depth = layer.bottom_depth - soil.curr_layer_depth
        soil.curr_layer_depth += depth

        soil_volume = depth * 10 * soil.area
        soil_mass = (layer.bulk_density / 0.001) * soil_volume

        # aggregate Soil Carbon Pools (Active, Slow, and Passive) and CO2 Gas Flux.

        # carbon pool conversion to percentages and their aggregation (i.e., Total %C)
        # S.6.D.2
        C_active_percent = (layer.C_active / soil_mass)
        C_slow_percent = (layer.C_slow / soil_mass)
        C_passive_percent = (layer.C_passive / soil_mass)

        # S.6.D.3
        layer.C_percent = C_active_percent + C_slow_percent + C_passive_percent
        layer.org_C = layer.C_percent

        # total soil carbon
        # S.6.D.4
        layer.C = layer.C_active + layer.C_slow + layer.C_passive
        layer.C_mg = layer.C * 0.001
        layer.C_g = layer.C * 0.1

        # total CO2 Gas Aggregation
        # S.6.D.5
        AG_CO2_loss = layer.AG_met_to_C_active_loss + layer.AG_struct_to_C_active_loss + \
                      layer.AG_struct_to_C_slow_loss
        BG_CO2_loss = layer.BG_met_to_C_active_loss + layer.BG_struct_to_C_active_loss + \
                      layer.BG_struct_to_C_slow_loss

        # S.6.D.6
        layer.C_CO2_loss_decomp = layer.C_active_loss + layer.C_slow_loss + layer.C_passive_loss

        # S.6.D.7
        layer.C_CO2_loss = AG_CO2_loss + BG_CO2_loss + layer.C_CO2_loss_decomp

    soil.curr_layer_depth = 0
