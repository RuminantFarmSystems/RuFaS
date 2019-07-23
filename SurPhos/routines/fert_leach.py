
# estimates P leaching from surface fertilizer with rainfall and
# P infiltration into soil and loss in runoff

# fertilizer P adsorption by soil in KG

from math import log, exp


def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall
    runoff = weather.runoff

    if S.fert_CNT > 0.0:
        if S.cover == 1:
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.5333
        elif S.cover == 2:
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.6667
        elif S.cover == 3:
            sorp_percent = -0.16 * log(S.fert_CNT) + 0.8
    else:
        sorp_percent = 0.0

    if S.fert_sorp < 0.0:
        S.fert_sorp = 0.0
    if S.fert_sorp > S.fert_p_available:
        S.fert_sorp = S.fert_p_available

    S.fert_p_available -= S.fert_sorp

    if S.fert_p_available < 0.0:
        S.fert_p_available = 0.0

    S.fert_absorbed_sum += S.fert_sorp

    # convert soil P from KG/HA to KG and add fertilizer p adsorbed

    S.labile_P_layer[0] *= S.area
    S.labile_P_layer[0] += S.fert_sorp
    S.labile_P_layer[0] /= S.area

    S.fert_CNT += 1.0

    # P leached from fertilizer on surface to rain and runoff water in KG

    if rainfall[year][day - 1] > 0.0:
        S.no_rains += 1

        if S.no_rains == 1:
            S.fert_leach = S.fert_p_available
            S.fert_p_available = 0.0
        else:
            if S.no_rains == 2:
                S.fert_leach = S.fert_p_released * 0.40
            if S.no_rains > 2:
                S.fert_leach = S.fert_p_released * 0.075
            S.fert_p_released -= S.fert_leach

    else:
        S.fert_leach = 0.0

    # calculate the concentration of fertilizer dissolved P in runoff in MG/L

    if runoff[year][day - 1] > 0.0:
        S.PD_factor = 0.034 * exp((runoff[year][day - 1] / rainfall[year][day - 1]) * 3.4)
        S.fert_runoff_P = S.fert_leach / (rainfall[year][day - 1] / 10.0) \
                          / S.area * 10.0 * S.PD_factor

    # calculate fertilizer runoff P in KG

        fert_run = S.fert_runoff_P * runoff[year][day - 1] * 0.01 * S.area
        if fert_run < 0.0:
            fert_run = 0.0
        if fert_run > S.fert_leach:
            fert_run = S.fert_leach

    else:
        S.fert_runoff_P = 0.0
        fert_run = 0.0

    # convert soil P from KG/HA to KG and add fertilizer P leached

    S.labile_P_layer[0] *= S.area
    S.labile_P_layer[1] *= S.area
    S.labile_P_layer[2] *= S.area

    S.labile_P_layer[0] += (S.fert_leach - fert_run) * 0.6

    if S.depths_layer[1] <= 15.0:
        S.labile_P_layer[1] += (S.fert_leach - fert_run) * 0.3
        S.labile_P_layer[2] += (S.fert_leach - fert_run) * 0.1
    else:
        S.labile_P_layer[1] += (S.fert_leach - fert_run) * 0.4

    S.labile_P_layer[0] /= S.area
    S.labile_P_layer[1] /= S.area
    S.labile_P_layer[2] /= S.area

    # add fertilizer P leached and in runoff to running total

    S.fert_R_sum += fert_run
    S.fert_L_sum += (S.fert_leach - fert_run)


