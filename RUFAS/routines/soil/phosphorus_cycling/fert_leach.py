################################################################################
"""
SurPhos
File name: fert_leach.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           WIlliam Donovan, wmdonovan@wisc.edu
"""
################################################################################

# estimates P leaching from surface fertilizer with rainfall and
# P infiltration into soil and loss in runoff

# fertilizer P adsorption by soil in KG

from math import log, exp


def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall
    runoff = S.runoff

    sorp_percent = 0.0
    if S.fert_CNT > 0.0:
        if S.cover == "BARE":
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.5333
        elif S.cover == "RESIDUE COVER":
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.6667
        elif S.cover == "GRASSED":
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.8

    S.fert_sorp = max(0.0, S.fert_sorp)
    S.fert_sorp = min(S.fert_sorp, S.fert_P_available)

    S.fert_P_available -= S.fert_sorp

    S.fert_P_available = max(0.0, S.fert_P_available)

    S.fert_absorbed_sum += S.fert_sorp

    # convert soil P from KG/HA to KG and add fertilizer p adsorbed

    S.listOfSoilLayers[0].labile_P *= S.area
    S.listOfSoilLayers[0].labile_P += S.fert_sorp
    S.listOfSoilLayers[0].labile_P /= S.area

    S.fert_CNT += 1.0

    # P leached from fertilizer on surface to rain and runoff water in KG

    if rainfall[year - 1][day - 1] > 0.0:
        S.no_rains += 1

        if S.no_rains == 1:
            S.fert_leach = S.fert_P_available
            S.fert_P_available = 0.0
        else:
            if S.no_rains == 2:
                S.fert_leach = S.fert_P_released * 0.40
            if S.no_rains > 2:
                S.fert_leach = S.fert_P_released * 0.075
            S.fert_P_released -= S.fert_leach

    else:
        S.fert_leach = 0.0

    # calculate the concentration of fertilizer dissolved P in runoff in MG/L

    if runoff > 0.0:
        S.PD_factor = 0.034 * exp((runoff / rainfall[year - 1][day - 1]) * 3.4)
        S.fert_runoff_P = S.fert_leach / (rainfall[year - 1][day - 1] / 10.0) \
                          / S.area * 10.0 * S.PD_factor

        # calculate fertilizer runoff P in KG

        S.fert_run = S.fert_runoff_P * runoff * 0.01 * S.area
        S.fert_run = max(0.0, S.fert_run)
        S.fert_run = min(S.fert_run, S.fert_leach)
    else:
        S.fert_runoff_P = 0.0
        S.fert_run = 0.0

    # convert soil P from KG/HA to KG and add fertilizer P leached

    for w in range(0, 3):
        S.listOfSoilLayers[w].labile_P *= S.area

    S.listOfSoilLayers[0].labile_P += (S.fert_leach - S.fert_run) * 0.6

    if S.listOfSoilLayers[1].bottomDepth <= 15.0:
        S.listOfSoilLayers[1].labile_P += (S.fert_leach - S.fert_run) * 0.3
        S.listOfSoilLayers[2].labile_P += (S.fert_leach - S.fert_run) * 0.1
    else:
        S.listOfSoilLayers[1].labile_P += (S.fert_leach - S.fert_run) * 0.4

    for w in range(0, 3):
        S.listOfSoilLayers[w].labile_P /= S.area

    # add fertilizer P leached and in runoff to running total

    S.fert_R_sum += S.fert_run
    S.fert_L_sum += (S.fert_leach - S.fert_run)


