"""
SurPhos
File name: manure_leach.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
from math import exp


# this subroutine estimates P leaching from surface manure with rainfall
# and P infiltration into soil and loss in runoff
# "pseudocode_soil" S.5.G
def update_all(S, weather, time):

    day = time.day
    year = time.year
    rainfall = weather.rainfall[year - 1][day - 1]
    runoff = S.runoff
    temp = weather.T_avg[year - 1][day - 1]

    # Calculate manure factors
    # S.5.G.I

    # S.5.G.I.1
    TFA = max(0.0, (2.0 * 32.0 ** 2 * temp ** 2
                    - temp ** 4) / 32.0 ** 4)

    # P leached from manure on surface to rain and runoff water in KG

    # S.5.G.I.2
    S.MIP_leach = 0.0
    S.MOP_leach = 0.0
    S.MIP_runoff = 0.0
    S.MOP_runoff = 0.0
    MTF_1 = 1.2
    MTF_2 = 73.1  # TODO: These are the values for a dairy application. Temporarily hard coded.
    if S.manure_mass > 0.0 and S.manure_cov > 0.0:
        water_manure = rainfall / S.manure_mass \
                       * S.manure_cov * 10000.0

        # S.5.G.I.3
        manure_extr = 0.0
        if rainfall > 0.0:
            manure_extr = min(1.0, (MTF_1 * water_manure) / (water_manure + MTF_2))

        # Manure Phosphorus Leaching
        # S.5.G.II

        # S.5.G.II.1
        S.MIP_leach = min(max(0.0, manure_extr * S.WIP), S.WIP)
        S.MOP_leach = min(max(0.0, manure_extr * S.WOP / 0.6), S.WOP)

        # calculates the concentration of all dissolved P in runoff in MG/L
        if runoff > 0.0:

            # S.5.G.II.2
            S.PD_factor = (runoff / rainfall) ** 0.225

            # S.5.G.II.3
            S.MIP_runoff = min(
                    max(
                        0.0,
                        (S.MIP_leach / (rainfall / 10.0) / S.area * 10.0 * S.PD_factor) * 0.01 * S.area),
                    S.MIP_leach)

            S.MOP_runoff = min(
                    max(
                        0.0,
                        (S.MOP_leach / (rainfall / 10.0) / S.area * 10.0 * S.PD_factor) * runoff * 0.01 * S.area),
                    S.MOP_leach)

        # S.5.G.II.4
        S.MIP_leach -= S.MIP_runoff
        S.MOP_leach -= S.MOP_runoff

        S.WIP -= (S.MIP_leach + S.MIP_runoff)
        S.WOP -= (S.MIP_leach + S.MOP_runoff)

        S.MIP_leach_annual += S.MIP_leach
        S.MOP_leach_annual += S.MOP_leach
        S.M_leach = S.MIP_leach - S.MIP_runoff + S.MOP_leach - S.MOP_runoff
        S.M_leach_annual += S.M_leach
        # convert soil P from KG/HA to KG and add manure P leached

        DF = 0.6
        M_not_leached = S.M_leach
        for layer in S.soil_layers:
            layer.labile_P *= S.area

            layer.labile_P += DF * S.M_leach
            M_not_leached -= DF * S.M_leach

            layer.labile_P /= S.area

            DF = max(0.0, (DF / 2) - 0.02)

        S.DRP_leach_annual += M_not_leached

        S.MIP_runoff_annual += S.MIP_runoff
        S.MOP_runoff_annual += S.MOP_runoff

        S.MIP_leach_annual += S.MIP_leach
        S.MOP_leach_annual += S.MOP_leach

        # Manure Decomposition
        # S.5.G.III

        # S.5.G.III.1
        wet_rate = -0.3 * S.manure_moisture + 0.27
        dry_rate = (-0.05 *
                    (0 if S.manure_applied == 0 else (S.manure_mass / S.manure_applied)) +
                    0.075) * TFA

        # S.5.G.III.2
        if rainfall > 4.0:
            S.manure_moisture += wet_rate
        elif rainfall <= 1.0:
            S.manure_moisture -= dry_rate

        # S.5.G.III.3
        S.manure_moisture = min(0.9, max(0.0, S.manure_moisture))

        # S.5.G.III.4
        AWDCR = 0.003 * TFA ** 0.5
        ASIM = 30.0 * exp(2.5 * S.manure_moisture)

        # S.5.G.III.5
        d_com = min(max(0.0, S.manure_mass * AWDCR), S.manure_mass)

        # S.5.G.III.6
        cov_d_com = min(max(0.0, d_com / S.manure_mass * S.manure_cov), S.manure_cov)

        # S.5.G.III.7
        SIP_d_com = min(S.SIP, max(0.0, S.SIP * 0.0025 * min(TFA, S.manure_moisture)))
        SOP_d_com = min(S.SOP, max(0.0, S.SOP * 0.01 * min(TFA, S.manure_moisture)))
        WOP_d_com = min(S.WOP, max(0.0, S.WOP * 0.1 * min(TFA, S.manure_moisture)))

        # S.5.G.III.8
        man_ASIM = min(S.manure_mass, max(0.0, ASIM * TFA * S.manure_cov))

        # S.5.G.III.9
        cov_ASIM = min(S.manure_cov, max(0.0, man_ASIM / S.manure_mass * S.manure_cov))

        # S.5.G.III.10
        WIP_ASIM = min(S.WIP, max(0.0, man_ASIM / S.manure_mass * S.WIP))
        WOP_ASIM = min(S.WOP, max(0.0, man_ASIM / S.manure_mass * S.WOP))
        SIP_ASIM = min(S.WIP, max(0.0, man_ASIM / S.manure_mass * S.SIP))
        SOP_ASIM = min(S.SOP, max(0.0, man_ASIM / S.manure_mass * S.SOP))

        S.SOP = max(0.0, S.SOP - SOP_ASIM - SOP_d_com)
        S.WOP = max(0.0, S.WOP - WOP_ASIM - WOP_d_com)
        S.SIP = max(0.0, S.SIP - SIP_ASIM - SIP_d_com)
        S.WIP = max(0.0, S.WIP - WIP_ASIM)

        # Decomposition and assimilation transfer between pools in some cases
        # S.5.G.II.11
        S.WIP += WOP_d_com + SOP_d_com * 0.75 + SIP_d_com
        S.WOP += SOP_d_com * 0.25

        # Total decomposed P
        # S.5.G.III.12
        S.DP = SIP_ASIM + WOP_ASIM + SOP_ASIM + WIP_ASIM

        # Update manure mass and cover to reflect decomposition
        # S.5.G.III.13
        S.manure_mass = max(0.0, S.manure_mass - d_com - man_ASIM)
        S.manure_cov = S.manure_cov - cov_d_com - cov_ASIM

        DF = 0.6
        DP_not_decomposed = S.DP
        for layer in S.soil_layers:
            # S.5.B.3
            layer.labile_P *= S.area

            # S.5.G.IV.14
            layer.labile_P += DF * S.DP
            DP_not_decomposed -= DF * S.DP

            # S.5.B.4
            layer.labile_P /= S.area

            DF = max(0.0, (DF / 2) - 0.02)

        S.DRP_leach_annual += DP_not_decomposed

    # calculate manure runoff P in MG/L
    # S.5.G.IV
    S.M_DRP_runoff = 0.0
    S.TIP_runoff = 0.0
    if runoff > 0.0:
        # S.5.G.IV.1
        layer = S.soil_layers[0]
        layer.soil_P = layer.labile_P / layer.bulk_density / layer.thickness_cm

        # S.5.G.IV.2/3
        S.M_DRP_runoff = layer.soil_P * 0.005
        S.TIP_runoff = S.MIP_runoff + S.M_DRP_runoff + S.fert_P_runoff

        S.M_DRP_runoff_annual += S.M_DRP_runoff
        S.TIP_runoff_annual += S.TIP_runoff
