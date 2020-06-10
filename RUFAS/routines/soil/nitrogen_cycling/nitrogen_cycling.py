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

    NO3 = initial NO3 levels (mg/kg)

    z = depth of the soil layer's lower boundary

    OrgN = initial Organic N (Active + Stable) (mg/kg)

    OrgC = Organic carbon in a soil layer (%, user input)

    NH4 = initial NO4 levels (0 mg/kg)
    
    tempfac = temperature factor
    
    waterfac = water factor
    
    soilTemp = temperature of the soil layer (ºC)
    
    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H2O)

    WP = soil water content held at wilting point (mm H2O)

    FC = field capacity (mm H2O)
    
    SAT = saturated water content of the soil layer (mm H2O)

    DepthFac = volatilization depth factor

    z_mid = 5mm (assuming a 10mm top layer)

    NitrReg = nitrification regulator

    VolatilReg = volatilization regulator

    CECFac = volatilization cation exchange factor (0.15)

    TotNitriVolatil = total combined nitrification and volatilization (kg/ha)

    FracNitr = fraction of total that is nitrification

    FracVolatil = fraction of total that is volatilization

    Nitrification = mass of nitrification (kg/ha)

    Volatilization = mass of Volatilization

    NO3/NH4Conc1 = concentration of NO3 or NH4 in the top soil layer (kg N/mm H2O)

    w = sum of runoff and soil water for the layer

    NO3/NH4Runoff = mass of NO3 or NH4 loss in runoff from soil layer 1 (kg/ha)

    Cr = coefficient of extraction for runoff (0.1)

    NConc = concentration of nitrogen loss in erosion for each pool except
                    NO3 (mg/kg)

    BD = soil layer bulk density (g/cm^3)

    depth = soil layer thickness (mm)

    Eros_N_Loss = N mass loss in erosion for each pool(kg/ha)

    Sed = daily soil loss (Metric Tons/ha)

    ER = enrichment ratio

    NO3/NH4Conc = concentration of NO3 or NH4 for leaching (kg N / mm H2O)

    NO3/NH4Perc = mass of NO3 or NH4 loss in percolation water from all soil layers
                (kg/ha)

    DenitrN = denitrification (kg/ha)

    deNrate = user defined denitrification rate coefficient (0.1)

    OrgC = soil organic matter content (%)

    Nminact = mineralization from active N pool (kg/ha)

    CN = daily rate constant, ratio of Carbon to Nitrogen

    CP = ratio of the residue

    Decay = decay rate constant defining the fraction of residue decomposed

    minCoeff = fresh residue mineralization coefficient (0.05)

    resComp = nutrient cycling residue decomposition factor

    FreshMin = mineralization of Fresh N (kg/ha)

    Ntrans = nitrogen transferred between the active and stable pools

    FracN = fraction of humic nitrogen in the active pool (0.02)


Soil values updated by calling update_all():

    soil_layers

    values updated in each soil layer:

        NO3
        NH4
        temp_fac
        water_fac
        volatilization
        activeN
        orgN
        stableN


"""

###############################################################################

from math import exp
from . import denitrification, humus_mineralization, mineralization_decomp, \
    leaching_runoff_erosion, nitrification_volatilization


#
# This function calls all the necessary functions to update information related
# to nitrogen cycling. The order in which each method is called is significant
# and is still being worked out.
#
def update_all(soil, weather, time):

    calc_temp_factors(soil)

    calc_water_factors(soil)

    nitrification_volatilization.nitrification_volatilization(soil)

    leaching_runoff_erosion.leaching_runoff_erosion(soil)

    denitrification.denitrification(soil)

    mineralization_decomp.mineralization_decomp(soil)

    humus_mineralization.humus_mineralization(soil)

    added_manure_N(soil, weather, time)


#
# Helper method used to calculate the temperature factor used to
# calculate nitrification, volatilization, denitrification, and mineralization
# for each layer
# "pseudocode_soil" S.4.B.1
#
def calc_temp_factors(soil):
    for layer in soil.soil_layers:
        soilTemp = layer.temperature

        exp_part = exp(9.93 - 0.312 * soilTemp)
        temp_fac = max(0, soilTemp / (soilTemp + exp_part))

        layer.temp_fac = temp_fac


#
# Helper method used to calculate the water factor used to
# calculate nitrification, volatilization, denitrification, and mineralization
# for each layer
# "pseudocode_soil" S.4.B.2
#
def calc_water_factors(soil):
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


def added_manure_N(soil, weather, time):
    totalN = weather.manureN[time.year - 1][time.day - 1]

    activeN = totalN * 0.875
    stableN = totalN * 0.125

    soil.soil_layers[0].activeN += activeN
    soil.soil_layers[0].stableN += stableN
