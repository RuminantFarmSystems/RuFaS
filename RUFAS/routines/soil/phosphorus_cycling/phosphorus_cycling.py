"""
RUFAS: Ruminant Farm Systems Model

phosphorus_cycling.py

Authors: DR. Peter A. Vadas
         USDA-ARS Dairy Forage Research Center
         1925 Linden Dr. West
         Madison, WI 53706
         PHONE NO. (608) 890-0069
         E-mail: peter.vadas@ars.usda.gov

Coders:  Jacob Johnson
         William Donovan
"""

from . import fert_leach, manure_leach, p_mineralization, soluble_P, erosion


def update_all(soil, weather, time):

    soluble_P.update_all(soil)

    fert_leach.update_all(soil, weather, time)

    manure_leach.update_all(soil, weather, time)

    p_mineralization.update_all(soil, time)

    erosion.update_all(soil)

    update_profile_P(soil)


def update_profile_P(soil):
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

    profile_P = soil.labile_P + soil.active_P + \
                soil.stable_P + soil.org_P

    soil.delta_P = profile_P - soil.profile_P

    soil.profile_P = profile_P

    soil.P_erosion = soil.sed_P

    soil.P_drainage = soil.fert_P_leach + soil.M_leach + soil.DRP_leach

    soil.P_runoff = soil.M_DRP_runoff + soil.fert_P_runoff_act + \
                    soil.DRP_runoff + soil.MIP_runoff + soil.MOP_runoff

    soil.P_calc = soil.delta_P + soil.P_erosion + soil.P_drainage + soil.P_runoff + soil.P_uptake

    soil.P_balance_difference = soil.manure_P_applied - soil.P_calc


def update_annual_P(soil):
    soil.manure_P_applied_annual += soil.manure_P_applied
    soil.P_erosion_annual += soil.P_erosion
    soil.P_drainage_annual += soil.P_drainage
    soil.P_runoff_annual += soil.P_runoff
    soil.P_uptake_annual += soil.P_uptake
