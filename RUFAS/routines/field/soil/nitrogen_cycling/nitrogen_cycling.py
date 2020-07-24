"""
RUFAS: Ruminant Farm Systems Model

File name: nitrogen_cycling.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: Nitrogen Cycling driver class.
             Calls the necessary functions for calculating and
             updating the content of three organic N pools (Fresh, Active, and
             Stable) and two inorganic pools (NO3 and NH4) associated with a
             soil profile on a given day 

Soil attribute definitions

    NO3 = initial NO3 levels (kg/ha)

    z = depth of the soil layer's lower boundary

    org_N = initial Organic N (Active + Stable) (kg/ha)

    org_C = Organic carbon in a soil layer (%, user input)

    NH4 = initial NO4 levels (0 mg/kg)
    
    temp_fac = temperature factor
    
    water_fac = water factor
    
    soil_temp = temperature of the soil layer (ºC)
    
    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H2O)

    WP = soil water content held at wilting point (mm H2O)

    FC = field capacity (mm H2O)
    
    SAT = saturated water content of the soil layer (mm H2O)

    depth_fac = volatilization depth factor

    z_mid = 5mm (assuming a 10mm top layer)

    nitr_reg = nitrification regulator

    volatil_reg = volatilization regulator

    CEC_fac = volatilization cation exchange factor (0.15)

    tot_nitri_volatil = total combined nitrification and volatilization (kg/ha)

    frac_nitr = fraction of total that is nitrification

    frac_volatil = fraction of total that is volatilization

    nitrification = mass of nitrification (kg/ha)

    volatilization = mass of volatilization

    NO3/NH4_conc1 = concentration of NO3 or NH4 in the top soil layer (kg N/mm H2O)

    w = sum of runoff and soil water for the layer

    NO3/NH4_runoff = mass of NO3 or NH4 loss in runoff from soil layer 1 (kg/ha)

    Cr = coefficient of extraction for runoff (0.1)

    N_conc = concentration of nitrogen loss in erosion for each pool except
                    NO3 (mg/kg)

    BD = soil layer bulk density (g/cm^3)

    depth = soil layer thickness (mm)

    eros_N_loss = N mass loss in erosion for each pool(kg/ha)

    sed = daily soil loss (Metric Tons/ha)

    ER = enrichment ratio

    NO3/NH4_conc = concentration of NO3 or NH4 for leaching (kg N / mm H2O)

    NO3/NH4_perc = mass of NO3 or NH4 loss in percolation water from all soil layers
                (kg/ha)

    denitr_N = denitrified Nitrogen(kg/ha)

    de_N_rate = user defined denitrification rate coefficient (0.1)

    org_C = soil organic matter content (%)

    N_min_act = mineralization from active N pool (kg/ha)

    CN = daily rate constant, ratio of Carbon to Nitrogen

    CP = ratio of the residue

    decay = decay rate constant defining the fraction of residue decomposed

    min_coeff = fresh residue mineralization coefficient (0.05)

    res_comp = nutrient cycling residue decomposition factor

    fresh_min = mineralization of Fresh N (kg/ha)

    N_trans = nitrogen transferred between the active and stable pools

    frac_N = fraction of Humic Nitrogen in the active pool (0.02)
"""

from math import exp
from . import denitrification, humus_mineralization, mineralization_decomp, \
    leaching_runoff_erosion, nitrification_volatilization


def update_all(soil, manure_management, weather, time):
    """
    Description:
        This function calls all the necessary functions to update information related
        to nitrogen cycling. The order in which each method is called is significant
        and is a matter of active development.
    Args:
        soil: instance of the Soil class specified in soil.py
        manure_management: instance of the BaseApplicationManagement class
            specified in field_management.py representing the management scheme
            for manure applications
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    calc_temp_factors(soil)

    calc_water_factors(soil)

    nitrification_volatilization.nitrification_volatilization(soil)

    leaching_runoff_erosion.leaching_runoff_erosion(soil)

    denitrification.denitrification(soil)

    mineralization_decomp.mineralization_decomp(soil)

    humus_mineralization.humus_mineralization(soil)

    if (time.start_year + time.year - 1, time.day) in manure_management.applications:
        if manure_management.check_conditions(soil, weather, time):
            added_manure_N(soil, manure_management.applications[(time.start_year + time.year - 1,
                                                                 time.day)].data)


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


def added_manure_N(soil, manure_application):
    """
    Description:
        TODO: Temporary method pending link to manure storage
        Adds specified manure to soil with no availability constraints.

    Args:
        soil
        manure_application: an instance of the BaseApplication object specified in
            field_management.py representing a manure application
    """

    total_N = manure_application['mass'] * manure_application['N_frac']
    active_N = total_N * 0.875
    stable_N = total_N * 0.125

    soil.soil_layers[0].active_N += active_N
    soil.soil_layers[0].stable_N += stable_N
