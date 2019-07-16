
# estimates P leaching from surface fertilizer with rainfall and
# P infiltration into soil and loss in runoff

# fertilizer P adsorption by soil in KG

from math import log


def update_all(surphos, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall
    runoff = weather.runoff

    if surphos.fert_CNT > 0.0:
        if surphos.cover == 1:
            sorp_percent = -0.16 * log(surphos.fert_CNT) + 0.5333
        elif surphos.cover == 2:
            sorp_percent = -0.16 * log(surphos.fert_CNT) + 0.6667
        elif surphos.cover == 3:
            sorp_percent = -0.16 * log(surphos.fert_CNT) + 0.8
    else:
        sorp_percent = 0.0

    if surphos.fert_sorp < 0.0:
        surphos.fert_sorp = 0.0
    if surphos.fert_sorp > surphos.fert_p_available:
        surphos.fert_sorp = surphos.fert_p_available

    surphos.fert_p_available -= surphos.fert_sorp

    if surphos.fert_p_available < 0.0:
        surphos.fert_p_available = 0.0

    surphos.fert_absorbed_sum += surphos.fert_sorp

    # convert soil P from KG/HA to KG and add fertilizer p adsorbed

    surphos.labile_P_layer[1] *= surphos.area
    surphos.labile_P_layer[1] += surphos.fert_sorp
    surphos.labile_P_layer[1] /= surphos.area

    surphos.fert_CNT += 1.0

    # P leached from fertilizer on surface to rain and runoff water in KG

    if rainfall[year][day] > 0.0:
        surphos.no_rains += 1

        if surphos.no_rains == 1:
            surphos.fert_leach = surphos.fert_p_available
            surphos.fert_p_available = 0.0
        else:
            if surphos.no_rains == 2:
                surphos.fert_leach = surphos.fert_p_released * 0.40
            if surphos.no_rains > 2:
                surphos.fert_leach = surphos.fert_p_released * 0.075
            surphos.fert_p_released -= surphos.fert_leach

    else:
        surphos.fert_leach = 0.0

    # calculate the concentration of fertilizer dissolved P in runoff in MG/L

    # if runoff[year][day] > 0.0:
    #     surphos.PD_factor =
