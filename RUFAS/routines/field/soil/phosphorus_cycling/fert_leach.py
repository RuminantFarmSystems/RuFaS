################################################################################
"""
SurPhos
File name: fert_leach.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

from math import log, exp


# estimates P leaching from surface fertilizer with rainfall and
# P infiltration into soil and loss in runoff
# "pseudocode_soil" S.5.F
def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall[year - 1][day - 1]
    runoff = S.runoff

    # Sorption
    # S.5.F.I

    # S.5.F.I.1
    sorp_percent = 0.0
    if S.fert_CNT > 0.0:
        sorp_percent = -0.16 * log(S.fert_CNT) + S.cover_factor

    # S.5.F.I.2
    S.fert_sorp = min(max(0.0, S.fert_sorp), S.fert_P_available)

    S.fert_P_available -= S.fert_sorp
    S.fert_absorbed_sum += S.fert_sorp

    S.fert_CNT += 1.0

    # Runoff and Leaching
    # S.5.F.II

    # S.5.F.II.1
    if rainfall > 0.0:
        S.no_rains += 1

        release_factor = 0
        if S.no_rains == 1:
            release_factor = 1
        else:
            if S.no_rains == 2:
                release_factor = 0.4
            if S.no_rains > 2:
                release_factor = 0.075

        S.fert_leach = S.fert_P_available * release_factor
        S.fert_P_released -= S.fert_leach

    # calculate the concentration of fertilizer dissolved P in runoff in MG/L
    S.fert_runoff_P = 0.0
    S.fert_run = 0.0
    if runoff > 0.0:
        # S.5.F.II.2
        S.PD_factor = 0.034 * exp((runoff / rainfall) * 3.4)

        # S.5.F.II.3
        S.fert_runoff_P = S.fert_leach / (rainfall / 10.0) \
                          / S.area * 10.0 * S.PD_factor

        # calculate fertilizer runoff P in KG
        # S.5.F.II.4
        S.fert_run = min(max(0.0, S.fert_runoff_P * runoff * 0.01 * S.area), S.fert_leach)

    # convert soil P from KG/HA to KG and add fertilizer P leached to each layer
    # S.5.F.II.5
    DF = 0.6
    S.fert_leach -= S.fert_run
    fert_not_leached = S.fert_leach
    for layer in S.soil_layers:

        # S.5.B.3
        layer.labile_P *= S.area

        if S.soil_layers.index(layer) == 0:
            layer.labile_P += S.fert_sorp

        # S.5.F.II.5
        layer.labile_P += S.fert_leach * DF
        fert_not_leached -= S.fert_leach * DF
        DF = max(0.0, (DF / 2) - 0.02)

        # S.5.B.4
        layer.labile_P /= S.area

    S.DRP_leachate_annual += fert_not_leached

    # add fertilizer P leached and in runoff to running total
    S.fert_runoff_annual += S.fert_run
    S.fert_leachate_annual += S.fert_leach
