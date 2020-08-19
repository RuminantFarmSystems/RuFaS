"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Description: Nitrogen Cycling driver class.
             Calls the necessary functions for calculating and
             updating the content of three organic N pools (Fresh, Active, and
             Stable) and two inorganic pools (NO3 and NH4) associated with a
             soil profile on a given day

Author(s): William Donovan, wmdonovan@wisc.edu
"""

from math import exp
from . import denitrification, humus_mineralization, mineralization_decomp, \
    leaching_runoff_erosion, nitrification_volatilization


def update_all(soil, field_management):
    """
    Description:
        This function calls all the necessary functions to update information related
        to nitrogen cycling. The order in which each method is called is significant
        and is a matter of active development.
    Args:
        soil: instance of the Soil class specified in soil.py
        field_management: instance of the FieldManagement class specified in
            field_management.py
    """

    calc_temp_factors(soil)

    calc_water_factors(soil)

    nitrification_volatilization.nitrification_volatilization(soil)

    leaching_runoff_erosion.leaching_runoff_erosion(soil)

    denitrification.denitrification(soil)

    mineralization_decomp.mineralization_decomp(soil)

    humus_mineralization.humus_mineralization(soil)

    update_profile_N(soil, field_management)


def calc_temp_factors(soil):
    """
    Description:
        Helper method used to calculate the temperature factor used in the
        calculations for nitrification, volatilization, denitrification, and
        mineralization
        "pseudocode_soil" S.4.B.1
    Args:
        soil
    """

    for layer in soil.soil_layers:
        soil_temp = layer.temperature

        exp_part = exp(9.93 - 0.312 * soil_temp)
        temp_fac = max(0, soil_temp / (soil_temp + exp_part))

        layer.temp_fac = temp_fac


def calc_water_factors(soil):
    """
    Description:
        Helper method used to calculate the water factor used in the
        calculations for nitrification, volatilization, denitrification, and
        mineralization
        "pseudocode_soil" S.4.B.2
    Args:
        soil
    """

    for layer in soil.soil_layers:
        SW = layer.soil_water
        FC = layer.fc_water
        WP = layer.wilting_water
        SAT = layer.sat_water

        if SW > FC:
            water_fac = (SAT - SW) / (SAT - FC)
        else:
            water_fac = (SW - WP) / (FC - WP)

        layer.water_fac = water_fac


def update_profile_N(soil, field_management):
    soil.NH4 = 0.0
    soil.NO3 = 0.0
    soil.org_N = 0.0
    soil.active_N = 0.0
    soil.stable_N = 0.0
    soil.N_uptake = 0.0
    for layer in soil.soil_layers:
        soil.NH4 += layer.NH4
        layer.NH4_average += layer.NH4
        soil.NO3 += layer.NO3
        layer.NO3_average += layer.NO3
        soil.org_N += layer.org_N
        layer.org_N_average += layer.org_N
        soil.active_N += layer.active_N
        layer.active_N_average += layer.active_N
        soil.stable_N += layer.stable_N
        layer.stable_N_average += layer.stable_N
        soil.N_uptake += layer.N_uptake

    profile_N = soil.NH4 + soil.NO3 + soil.org_N + soil.fresh_N

    soil.delta_N = profile_N - soil.profile_N

    soil.profile_N = profile_N

    soil.N_drainage = soil.NH4_drainage + soil.NO3_drainage + \
                      soil.active_N_drainage

    soil.N_runoff = soil.NH4_runoff + soil.NO3_runoff

    soil.N_erosion = soil.NH4_erosion + soil.active_N_erosion + \
                     soil.fresh_N_erosion

    soil.N_calc = soil.delta_N + soil.N_drainage + soil.N_runoff + soil.N_erosion + soil.N_uptake

    soil.N_balance_difference = field_management.manure_N_applied - soil.N_calc


def update_annual_N(soil):
    soil.profile_N_average += soil.profile_N
    soil.fresh_N_average += soil.fresh_N
    soil.NO3_drainage_annual += soil.NO3_drainage
    soil.NH4_drainage_annual += soil.NH4_drainage
    soil.M_leach_annual += soil.M_leach
    soil.active_N_drainage_annual += soil.active_N_drainage
    soil.NO3_runoff_annual += soil.NO3_runoff
    soil.NH4_runoff_annual += soil.NH4_runoff
    soil.N_runoff_annual += soil.N_runoff
    soil.N_drainage_annual += soil.N_drainage
    soil.N_erosion_annual += soil.N_erosion
    soil.N_uptake_annual += soil.N_uptake
