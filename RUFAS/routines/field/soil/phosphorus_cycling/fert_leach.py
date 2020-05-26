"""
RUFAS
SurPhos

File name: fert_leach.py

Author(s):  DR. Peter A. Vadas
            USDA-ARS Dairy Forage Research Center
            E-mail: peter.vadas@ars.usda.gov

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""

from math import exp


def update_all(soil, weather, time):
    """
    Description:
        estimates P leaching from surface fertilizer with rainfall and
        P infiltration into soil and loss in runoff
        "pseudocode_soil" S.5.F

    Args:
        soil: instance of the Soil class specified in soil.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    day = time.day
    year = time.year
    rainfall = weather.rainfall[year - 1][day - 1]
    runoff = soil.runoff

    # Sorption
    # S.5.F.I

    # S.5.F.I.1
    # TODO: sorp_percent is unused. Vadas indicated there is a missing equation
    # sorp_percent = 0.0
    if soil.fert_CNT > 0.0:
        # sorp_percent = -0.16 * log(soil.fert_CNT) + soil.cover_factor
        pass

    # S.5.F.I.2
    soil.fert_sorp = min(max(0.0, soil.fert_sorp), soil.fert_P_available)

    soil.fert_P_available -= soil.fert_sorp
    soil.fert_absorbed_sum += soil.fert_sorp

    soil.fert_CNT += 1.0

    # Runoff and Leaching
    # S.5.F.II

    # S.5.F.II.1
    if rainfall > 0.0:
        soil.no_rains += 1

        release_factor = 0
        if soil.no_rains == 1:
            release_factor = 1
        else:
            if soil.no_rains == 2:
                release_factor = 0.4
            if soil.no_rains > 2:
                release_factor = 0.075

        soil.fert_P_leachate = soil.fert_P_available * release_factor
        soil.fert_P_released -= soil.fert_P_leachate

    # calculate the concentration of fertilizer dissolved P in runoff in MG/L
    soil.fert_P_runoff = 0.0
    soil.fert_P_runoff_act = 0.0
    if runoff > 0.0 and rainfall > 0.0:
        # S.5.F.II.2
        soil.PD_factor = 0.034 * exp((runoff / rainfall) * 3.4)

        # S.5.F.II.3
        soil.fert_P_runoff = soil.fert_P_leachate / (rainfall / 10.0) / soil.area * 10.0 * soil.PD_factor

        # calculate fertilizer runoff P in KG
        # S.5.F.II.4

        soil.fert_P_runoff_act = min(max(0.0, soil.fert_P_runoff * runoff * 0.01 * soil.area), soil.fert_P_leachate)

    # convert soil P from KG/HA to KG and add fertilizer P leached to each layer
    # S.5.F.II.5
    DF = 0.6
    soil.fert_P_leachate -= soil.fert_P_runoff_act
    fert_not_leached = soil.fert_P_leachate

    for layer in soil.soil_layers:

        # S.5.B.3
        layer.labile_P *= soil.area

        if soil.soil_layers.index(layer) == 0:
            layer.labile_P += soil.fert_sorp

        # S.5.F.II.5
        layer.labile_P += soil.fert_P_leachate * DF
        fert_not_leached -= soil.fert_P_leachate * DF
        DF = max(0.0, (DF / 2) - 0.02)

        # S.5.B.4
        layer.labile_P /= soil.area

    soil.DRP_leachate_annual += fert_not_leached

    # add fertilizer P leached and in runoff to running total
    soil.fert_runoff_annual += soil.fert_P_runoff_act
    soil.fert_P_leachate_annual += soil.fert_P_leachate
