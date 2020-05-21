"""
RUFAS
SurPhos

File name: manure_leach.py

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
        this subroutine estimates P leaching from surface manure with rainfall
        and P infiltration into soil and loss in runoff
        "pseudocode_soil" S.5.G
    Args:
        soil: instance of the Soil class specified in soil.py
        weather: instance of the Weather class specified in classes.py
        time: instance of the Time class specified in classes.py
    """

    day = time.day
    year = time.year
    rainfall = weather.rainfall[year - 1][day - 1]
    runoff = soil.runoff
    temp = weather.T_avg[year - 1][day - 1]

    # Calculate manure factors
    # S.5.G.I

    # S.5.G.I.1
    TFA = max(0.0, (2.0 * 32.0 ** 2 * temp ** 2
                    - temp ** 4) / 32.0 ** 4)

    # P leached from manure on surface to rain and runoff water in KG

    # S.5.G.I.2
    soil.MIP_leach = 0.0
    soil.MOP_leach = 0.0
    soil.MIP_runoff = 0.0
    soil.MOP_runoff = 0.0
    MTF_1 = 1.2
    MTF_2 = 73.1  # TODO: These are the values for a dairy application. Temporarily hard coded.
    if soil.manure_mass > 0.0 and soil.manure_cov > 0.0:
        water_manure = rainfall / soil.manure_mass \
                       * soil.manure_cov * 10000.0

        # S.5.G.I.3
        manure_extr = 0.0
        if rainfall > 0.0:
            manure_extr = min(1.0, (MTF_1 * water_manure) / (water_manure + MTF_2))

        # Manure Phosphorus Leaching
        # S.5.G.II

        # S.5.G.II.1
        soil.MIP_leach = min(max(0.0, manure_extr * soil.WIP), soil.WIP)
        soil.MOP_leach = min(max(0.0, manure_extr * soil.WOP / 0.6), soil.WOP)

        # calculates the concentration of all dissolved P in runoff in MG/L
        if runoff > 0.0:
            # S.5.G.II.2
            soil.PD_factor = (runoff / rainfall) ** 0.225

            # S.5.G.II.3
            soil.MIP_runoff = \
                min(
                    max(
                        0.0,
                        (soil.MIP_leach / (rainfall / 10.0) / soil.area * 10.0 * soil.PD_factor) * 0.01 * soil.area
                    ),
                    soil.MIP_leach
                )

            soil.MOP_runoff = \
                min(
                    max(
                        0.0,
                        ((soil.MOP_leach / (rainfall / 10.0) / soil.area * 10.0 * soil.PD_factor)
                         * runoff * 0.01 * soil.area)
                    ),
                    soil.MOP_leach
                )

        # S.5.G.II.4
        soil.MIP_leach -= soil.MIP_runoff
        soil.MOP_leach -= soil.MOP_runoff

        soil.WIP -= (soil.MIP_leach + soil.MIP_runoff)
        soil.WOP -= (soil.MIP_leach + soil.MOP_runoff)

        soil.MIP_leach_annual += soil.MIP_leach
        soil.MOP_leach_annual += soil.MOP_leach
        soil.M_leach = soil.MIP_leach - soil.MIP_runoff + soil.MOP_leach - soil.MOP_runoff
        # convert soil P from KG/HA to KG and add manure P leached

        DF = 0.6
        M_not_leached = soil.M_leach
        for layer in soil.soil_layers:
            layer.labile_P *= soil.area

            layer.labile_P += DF * soil.M_leach
            M_not_leached -= DF * soil.M_leach

            layer.labile_P /= soil.area

            DF = max(0.0, (DF / 2) - 0.02)

        soil.DRP_leachate_annual += M_not_leached

        soil.WIP_runoff_annual += soil.MIP_runoff
        soil.WOP_runoff_annual += soil.MOP_runoff

        soil.WIP_leachate_annual += soil.MIP_leach
        soil.WOP_leachate_annual += soil.MOP_leach

        # Manure Decomposition
        # S.5.G.III

        # S.5.G.III.1
        wet_rate = -0.3 * soil.manure_moisture + 0.27
        dry_rate = (-0.05 * (soil.manure_mass / soil.manure_mass_app) + 0.075) * TFA

        # S.5.G.III.2
        if rainfall > 4.0:
            soil.manure_moisture += wet_rate
        elif rainfall <= 1.0:
            soil.manure_moisture -= dry_rate

        # S.5.G.III.3
        soil.manure_moisture = min(0.9, max(0.0, soil.manure_moisture))

        # S.5.G.III.4
        AWDCR = 0.003 * TFA ** 0.5
        ASIM = 30.0 * exp(2.5 * soil.manure_moisture)

        # S.5.G.III.5
        d_com = min(max(0.0, soil.manure_mass * AWDCR), soil.manure_mass)

        # S.5.G.III.6
        cov_d_com = min(max(0.0, d_com / soil.manure_mass * soil.manure_cov), soil.manure_cov)

        # S.5.G.III.7
        SIP_d_com = min(soil.SIP, max(0.0, soil.SIP * 0.0025 * min(TFA, soil.manure_moisture)))
        SOP_d_com = min(soil.SOP, max(0.0, soil.SOP * 0.01 * min(TFA, soil.manure_moisture)))
        WOP_d_com = min(soil.WOP, max(0.0, soil.WOP * 0.1 * min(TFA, soil.manure_moisture)))

        # S.5.G.III.8
        man_ASIM = min(soil.manure_mass, max(0.0, ASIM * TFA * soil.manure_cov))

        # S.5.G.III.9
        cov_ASIM = min(soil.manure_cov, max(0.0, man_ASIM / soil.manure_mass * soil.manure_cov))

        # S.5.G.III.10
        WIP_ASIM = min(soil.WIP, max(0.0, man_ASIM / soil.manure_mass * soil.WIP))
        WOP_ASIM = min(soil.WOP, max(0.0, man_ASIM / soil.manure_mass * soil.WOP))
        SIP_ASIM = min(soil.WIP, max(0.0, man_ASIM / soil.manure_mass * soil.SIP))
        SOP_ASIM = min(soil.SOP, max(0.0, man_ASIM / soil.manure_mass * soil.SOP))

        soil.SOP = max(0.0, soil.SOP - SOP_ASIM - SOP_d_com)
        soil.WOP = max(0.0, soil.WOP - WOP_ASIM - WOP_d_com)
        soil.SIP = max(0.0, soil.SIP - SIP_ASIM - SIP_d_com)
        soil.WIP = max(0.0, soil.WIP - WIP_ASIM)

        # Decomposition and assimilation transfer between pools in some cases
        # S.5.G.II.11
        soil.WIP += WOP_d_com + SOP_d_com * 0.75 + SIP_d_com
        soil.WOP += SOP_d_com * 0.25

        # Total decomposed P
        # S.5.G.III.12
        soil.DP = SIP_ASIM + WOP_ASIM + SOP_ASIM + WIP_ASIM

        # Update manure mass and cover to reflect decomposition
        # S.5.G.III.13
        soil.manure_mass = max(0.0, soil.manure_mass - d_com - man_ASIM)
        soil.manure_cov = soil.manure_cov - cov_d_com - cov_ASIM

        DF = 0.6
        DP_not_decomposed = soil.DP
        for layer in soil.soil_layers:
            # S.5.B.3
            layer.labile_P *= soil.area

            # S.5.G.IV.14
            layer.labile_P += DF * soil.DP
            DP_not_decomposed -= DF * soil.DP

            # S.5.B.4
            layer.labile_P /= soil.area

            DF = max(0.0, (DF / 2) - 0.02)

        soil.DRP_leachate_annual += DP_not_decomposed

    # calculate manure runoff P in MG/L
    # S.5.G.IV
    soil.M_DRP_runoff = 0.0
    soil.TIP_runoff = 0.0
    if runoff > 0.0:
        # S.5.G.IV.1
        layer = soil.soil_layers[0]
        layer.soil_P = layer.labile_P / layer.bulk_density / layer.thickness_cm

        # S.5.G.IV.2/3
        soil.M_DRP_runoff = layer.soil_P * 0.005
        soil.TIP_runoff = soil.MIP_runoff + soil.M_DRP_runoff + soil.fert_P_runoff

        soil.M_DRP_runoff_annual += soil.M_DRP_runoff
        soil.TIP_runoff_annual += soil.TIP_runoff
