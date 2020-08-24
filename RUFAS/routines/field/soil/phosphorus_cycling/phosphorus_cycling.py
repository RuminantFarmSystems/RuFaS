"""
RUFAS: Ruminant Farm Systems Model

phosphorus_cycling.py

Author(s):  Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""

from . import fert_leach, manure_leach, P_mineralization, soluble_P, erosion


def update_all(soil, field_management, weather, time):
    """
    Description:
        Runs the phosphorus cycling sub-module.
        Currently largely based on Peter Vadas' SurPhos
    Args:
        soil: instance of the Soil class specified in soil.py
        field_management: instance of the FieldManagement class
            specified in field_management.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    # calculate soluble Phosphorus
    soluble_P.update_all(soil)

    # calculate leached fertilizer Phosphorus
    fert_leach.update_all(soil, weather, time)

    # calculate leached manure Phosphorus
    manure_leach.update_all(soil, field_management, weather, time)

    # calculate mineralized Phosphorus
    P_mineralization.update_all(soil, time)

    # calculate eroded Phosphorus
    erosion.update_all(soil)

    update_profile_P(soil, field_management)


def update_profile_P(soil, field_management):
    soil.labile_P = 0.0
    soil.active_P = 0.0
    soil.stable_P = 0.0
    soil.org_P = 0.0
    soil.soil_P = 0.0
    soil.P_uptake = 0.0

    for layer in soil.soil_layers:
        soil.labile_P += layer.labile_P
        soil.active_P += layer.active_P
        soil.stable_P += layer.stable_P
        soil.org_P += layer.org_P
        soil.soil_P += layer.soil_P
        soil.P_uptake += layer.P_uptake

    soil.STP = soil.soil_layers[0].labile_P + soil.soil_layers[0].active_P + soil.soil_layers[0].stable_P

    profile_P = soil.labile_P + soil.active_P + \
                soil.stable_P + soil.org_P

    soil.delta_P = profile_P - soil.profile_P

    soil.profile_P = profile_P

    soil.P_erosion = soil.sed_P

    soil.P_drainage = soil.fert_P_leached + soil.M_leach + soil.DRP_drainage

    soil.P_runoff = soil.M_DRP_runoff + soil.fert_P_runoff_act + \
                    soil.DRP_runoff + soil.MIP_runoff + soil.MOP_runoff

    soil.P_calc = soil.delta_P + soil.P_erosion + soil.P_drainage + soil.P_runoff + soil.P_uptake

    soil.P_balance_difference = field_management.manure_P_applied - soil.P_calc


def update_annual_P(soil):
    soil.M_DRP_runoff_annual += soil.M_DRP_runoff
    soil.TIP_runoff_annual += soil.TIP_runoff
    soil.MIP_leach_annual += soil.MIP_leach
    soil.MOP_leach_annual += soil.MOP_leach
    soil.fert_P_runoff_annual += soil.fert_P_runoff_act
    soil.fert_P_leached_annual += soil.fert_P_leached
    soil.DRP_runoff_annual += soil.DRP_runoff
    soil.DRP_drainage_annual += soil.DRP_drainage
    soil.P_erosion_annual += soil.P_erosion
    soil.P_drainage_annual += soil.P_drainage
    soil.P_runoff_annual += soil.P_runoff
    soil.P_uptake_annual += soil.P_uptake
    soil.STP_annual += soil.STP
