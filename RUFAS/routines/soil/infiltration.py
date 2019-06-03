'''
RUFAS: Ruminant Farm Systems Model

File name: infiltration.py

Author(s): William Donovan, wmdonovan@wisc.edu

Description: This module contains the necessary functions for calculating and
             updating water infiltration into the soil on a given day using the
             curve number approach. Currently the only function meant to be
             used outside of this file is the update_all() function. The other
             functions are meant to serve as helper functions within this file.

Soil attribute definitions

    Q = daily runoff (mm H20)

    R = daily rainfall depth (mm H20)

    S = retention parameter (mm H20)

    Smax = maximum value for S on any given day (mm H20)

    CN1 = Curve Number 1 (empirical value used to determine the retention
                            parameter S)

    CN2 = Curve Number 2

    CN3 = Curve Number 3

    Smax = maximum value for S on any given day (mm H20)

    SW = soil water content of entire profile, excluding water held at wilting
            point (mm H20)

    w1 = shape coefficient

    w2 = shape coefficient

    FC = amount of water in soil profile at field capacity (mm H20)

    SAT = amount of water in soil profile at saturation (mm H20)

    Sfrz = retention parameter when the top layer of soil is frozen


Soil values updated by calling update_all():
    soil.runoff
    soil.dayInfiltration
'''
###############################################################################

from math import exp, log


#
# This function calls all the necessary functions to update information related
# to infiltration
#
def update_all(soil, weather, time):

    calc_Q(soil, weather, time)

    calc_daily_infiltration(soil, weather, time)


#
# Calculates the daily runoff Q (mm H20)
# "pseudocode_SC_soilhydrology.docx" 2.A.1
#
def calc_Q(soil, weather, time):
    R = weather.rainfall[time.year-1][time.day-1]
    S = calc_S(soil)

    # modifies S if the top layer of soil is frozen
    # "pseudocode_SC_soilhydrology.docx" 2.A.9
    if soil.listOfSoilLayers[0].temperature <= 2:
        Smax = calc_Smax(soil)
        exp_part = exp(-0.000862 * S)
        S = Smax * (1 - exp_part)

    Q = 0.0
    if R > 0.2 * S:
        Q = ((R - 0.2 * S) ** 2) / (R + 0.8 * S)

    soil.runoff = Q


#
# Calculates the retention parameter S (mm H20) for use in calculating daily
# runoff (mm H20)
# "pseudocode_SC_soilhydrology.docx" 2.A.4
#
def calc_S(soil):
    CN3 = calc_CN3(soil)

    Smax = calc_Smax(soil)

    w2 = calc_w2(soil, Smax, CN3)
    w1 = calc_w1(soil, Smax, CN3, w2)

    SW = sum_SW(soil) - sum_WW(soil)

    S_exp = exp(w1 - (w2 * SW))

    return Smax * (1 - (SW / (SW + S_exp)))


#
# Calculates Curve Number 1 for use in calculating Smax
# "pseudocode_SC_soilhydrology.docx" 2.A.2
#
def calc_CN1(soil):
    CN2 = soil.CN2
    CN1_exp = exp(2.533 - 0.0636 * (100 - CN2))
    return CN2 - (20 * (100 - CN2)) / (100 - CN2 + CN1_exp)


#
# Calculates Curve Number 3 for use in calculating S3
# "pseudocode_SC_soilhydrology.docx" 2.A.3
#
def calc_CN3(soil):
    CN2 = soil.CN2
    CN3_exp = exp(0.00673 * (100 - CN2))
    return CN2 * CN3_exp


#
# Calculates Smax, the maximum value for S on any given day (mm H20)
# "pseudocode_SC_soilhydrology.docx" 2.A.5
#
def calc_Smax(soil):
    CN1 = calc_CN1(soil)
    return 25.4 * ((1000 / CN1) - 10)


#
# Calculates the shape coefficient w1
# "pseudocode_SC_soilhydrology.docx" 2.A.6
#
def calc_w1(soil, Smax, CN3, w2):
    FC = soil.profileDepth * soil.listOfSoilLayers[0].fieldCapacity

    S3 = calc_S3(CN3)

    log_part = log(FC / (1 - S3 * (1 / Smax)) - FC)

    return log_part + (w2 * FC)


#
# Calculates the shape coefficient w2
# "pseudocode_SC_soilhydrology.docx" 2.A.7
#
def calc_w2(soil, Smax, CN3):
    FC = soil.profileDepth * soil.listOfSoilLayers[0].fieldCapacity

    SAT = soil.profileDepth * soil.listOfSoilLayers[0].saturation

    S3 = calc_S3(CN3)

    l1 = log(FC / (1 - S3 * (1 / Smax)) - FC)
    l2 = log(SAT / (1 - 2.54 * (1 / Smax)) - SAT)

    return (l1 - l2) / (SAT - FC)


#
# Calculates S3 for use in calculating shape coefficients w1/w2
# "pseudocode_SC_soilhydrology.docx" 2.A.8
#
def calc_S3(CN3):
    return 25.4 * ((1000 / CN3) - 10)


#
# Calculates soil water content of the entire profile for use in calculating S
# "pseudocode_SC_soilhydrology.docx" 2.A.4
#
def sum_SW(soil):
    SW = 0.0
    for layer in soil.listOfSoilLayers:
        SW += layer.currentSoilWaterMM
    return SW


#
# Calculates the quantity of water held at wilting point in the entire profile
# for use in calculating S
# "pseudocode_SC_soilhydrology.docx" 2.A.4
#
def sum_WW(soil):
    WW = 0.0
    for layer in soil.listOfSoilLayers:
        WW += layer.wiltingWater
    return WW


#
# Calculates and updates daily infiltration as rainfall - runoff
# "pseudocode_SC_soilhydrology.docx" 2.A.10
#
def calc_daily_infiltration(soil, weather, time):
    rainfall = weather.rainfall[time.year-1][time.day-1]
    soil.dailyInfiltration = rainfall - soil.runoff
    SAT = soil.listOfSoilLayers[0].satWater
    SW = soil.listOfSoilLayers[0].currentSoilWaterMM

    soil.listOfSoilLayers[0].currentSoilWaterMM = min(SAT, soil.dailyInfiltration + SW)
