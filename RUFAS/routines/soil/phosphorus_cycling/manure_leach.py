################################################################################
"""
SurPhos
File name: manure_leach.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           WIlliam Donovan, wmdonovan@wisc.edu
"""
################################################################################

# this subroutine estimates P leaching from surface manure with rainfall
# and P infiltration into soil and loss in runoff

from math import exp


def update_all(S, weather, time):

    day = time.day
    year = time.year

    rainfall = weather.rainfall
    runoff = S.runoff
    temp = weather.T_avg

    TFA = max(0.0, (2.0 * 32.0 ** 2 * temp[year - 1][day - 1] ** 2
                    - temp[year - 1][day - 1] ** 4) / 32.0 ** 4)

    for w in range(0, 3):
        S.listOfSoilLayers[w].active_P *= S.area
        S.listOfSoilLayers[w].labile_P *= S.area

    # P leached from manure on surface to rain and runoff water in KG

    if S.manure_mass > 0.0 and S.manure_cov > 0.0:
        water_manure = rainfall[year - 1][day - 1] / S.manure_mass \
                       * S.manure_cov * 10000.0

        manure_extr = 0.0
        NH4_extr = 0.0
        if rainfall[year - 1][day - 1] > 0.0:

            if S.manure_type == "DAIRY":
                manure_extr = min(1.0, 1.2 * water_manure / (water_manure + 73.1))
                # manure_extr = min(1.0, 0.0000144 * water_manure ** 2.0285)
                NH4_extr = min(1.0, 0.9 * water_manure / (water_manure + 7.1))
            else:
                manure_extr = min(1.0, 2.2 * water_manure / (water_manure + 300.1))
                NH4_extr = 0.0  # TODO I added this

        MIP_leach = max(0.0, manure_extr * S.WIP)
        MOP_leach = max(0.0, manure_extr * S.WOP / 0.6)
        NH4_leach = max(0.0, NH4_extr * S.NH4)

        MIP_leach = min(MIP_leach, S.WIP)
        MOP_leach = min(MOP_leach, S.WOP)
        NH4_leach = min(NH4_leach, S.NH4)  # TODO changed from MOP_leach to NH4_leach

        S.WIP = max(0.0, S.WIP - MIP_leach)
        S.WOP = max(0.0, S.WOP - MOP_leach)
        S.NH4 = max(0.0, S.NH4 - NH4_leach)  # TODO: this is redundant

        S.TIP_leach += MIP_leach
        S.TOP_leach += MOP_leach
        S.TN_leach += NH4_leach

        # calculates the concentration of all dissolved P in runoff in MG/L

        runoff_MIP = 0.0
        runoff_MOP = 0.0
        runoff_MNH = 0.0
        S.runoff_IP = 0.0
        S.runoff_OP = 0.0
        S.runoff_NH = 0.0
        if runoff > 0.0:

            S.PD_factor = (runoff / rainfall[year - 1][day - 1]) ** 0.225
            S.ND_factor = runoff / rainfall[year - 1][day - 1]
            # S.ND_factor = 0.034 * exp((runoff / rainfall[year - 1][day - 1]) * 3.4)

            S.runoff_IP = MIP_leach / (rainfall[year - 1][day - 1] / 10.0) / S.area * 10.0 * S.PD_factor
            S.runoff_OP = MOP_leach / (rainfall[year - 1][day - 1] / 10.0) / S.area * 10.0 * S.PD_factor
            S.runoff_NH = NH4_leach / (rainfall[year - 1][day - 1] / 10.0) / S.area * 10.0 * S.ND_factor

            # calculate manure runoff P in KG

            runoff_MIP = max(0.0, S.runoff_IP * runoff * 0.01 * S.area)
            runoff_MOP = max(0.0, S.runoff_OP * runoff * 0.01 * S.area)
            runoff_MNH = max(0.0, S.runoff_NH * runoff * 0.01 * S.area)

            runoff_MIP = min(runoff_MIP, MIP_leach)
            runoff_MOP = min(runoff_MOP, MOP_leach)
            runoff_MNH = min(runoff_MNH, NH4_leach)

        # convert soil P from KG/HA to KG and add manure P leached

        # TODO math
        S.listOfSoilLayers[0].labile_P += 0.6 * (MIP_leach - runoff_MIP + MOP_leach - runoff_MOP)

        if S.listOfSoilLayers[1].bottom_depth_cm <= 15.0:

            # TODO math
            S.listOfSoilLayers[1].labile_P += 0.3 * (MIP_leach - runoff_MIP + MOP_leach - runoff_MOP)
            S.listOfSoilLayers[2].labile_P += 0.1 * (MIP_leach - runoff_MIP + MOP_leach - runoff_MOP)

        else:

            # TODO math
            S.listOfSoilLayers[1].labile_P += 0.4 * (MIP_leach - runoff_MIP + MOP_leach - runoff_MOP)

        # add manure P leached and in runoff to running total

        S.WIP_R_sum += runoff_MIP
        S.WOP_R_sum += runoff_MOP
        S.NH4_R_sum += S.runoff_NH
        S.WIP_L_sum += (MIP_leach - runoff_MIP)
        S.WOP_L_sum += (MOP_leach - runoff_MOP)
        S.NH4_L_sum += (NH4_leach - runoff_MNH)

        # decompose manure and manure P in KG

        wet = -0.3 * S.moisture + 0.27
        dry = (-0.05 * (S.manure_mass / S.manure_mass_app) + 0.075) * TFA

        if rainfall[year - 1][day - 1] > 4.0:
            S.moisture += wet
        elif rainfall[year - 1][day - 1] <= 1.0:
            S.moisture -= dry

        S.moisture = min(0.9, max(0.0, S.moisture))

        AWDCR = 0.003 * TFA ** 0.5
        ASIM = 30.0 * exp(2.5 * S.moisture)

        d_com = max(0.0, S.manure_mass * AWDCR)
        d_com = min(d_com, S.manure_mass)

        cov_d_com = max(0.0, d_com / S.manure_mass * S.manure_cov)
        cov_d_com = min(cov_d_com, S.manure_cov)

        # TODO should be commented out
        # SIP_d_com = max(0.0, S.SIP * 0.0025 * TFA * S.moisture)
        # if SIP_d_com > S.SIP:
        #     SIP_d_com = S.SIP
        # SOP_d_com = max(0.0, S.SOP * 0.01 * TFA * S.moisture)
        # if SOP_d_com > S.SOP:
        #     SOP_d_com = S.SOP
        # man_ASIM = max(0.0, S.manure_mass * 0.025 * TFA * S.moisture)
        # if man_ASIM > S.manure_mass:
        #     man_ASIM = S.manure_mass

        SIP_d_com = max(0.0, S.SIP * 0.0025 * min(TFA, S.moisture))
        SIP_d_com = min(SIP_d_com, S.SIP)

        SOP_d_com = max(0.0, S.SOP * 0.01 * min(TFA, S.moisture))
        SOP_d_com = min(SOP_d_com, S.SOP)

        SON_d_com = max(0.0, S.SON * 0.01 * min(TFA, S.moisture))
        SON_d_com = min(SON_d_com, S.SON)

        WOP_d_com = max(0.0, S.WOP * 0.1 * min(TFA, S.moisture))
        WOP_d_com = min(WOP_d_com, S.WOP)

        man_ASIM = max(0.0, ASIM * TFA * S.manure_cov)
        man_ASIM = min(man_ASIM, S.manure_mass)

        cov_ASIM = max(0.0, man_ASIM / S.manure_mass * S.manure_cov)
        cov_ASIM = min(cov_ASIM, S.manure_cov)  # TODO cov_ASIM was cov_d_com in min()

        WIP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.WIP)
        WIP_ASIM = min(WIP_ASIM, S.WIP)

        NH4_ASIM = max(0.0, man_ASIM / S.manure_mass * S.NH4)
        NH4_ASIM = min(NH4_ASIM, S.NH4)

        SIP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.SIP)
        SIP_ASIM = min(SIP_ASIM, S.SIP)

        WOP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.WOP)
        WOP_ASIM = min(WOP_ASIM, S.WOP)

        SOP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.SOP)
        SOP_ASIM = min(SOP_ASIM, S.SOP)

        SON_ASIM = max(0.0, man_ASIM / S.manure_mass * S.SON)
        SON_ASIM = min(SON_ASIM, S.SON)

        S.SOP = max(0.0, S.SOP - SOP_ASIM - SOP_d_com)
        S.SON = max(0.0, S.SON - SON_ASIM - SON_d_com)
        S.WOP = max(0.0, S.WOP - WOP_ASIM - WOP_d_com)
        S.SIP = max(0.0, S.SIP - SIP_ASIM - SIP_d_com)
        S.WIP = max(0.0, S.WIP - WIP_ASIM)
        S.NH4 = max(0.0, S.NH4 - NH4_ASIM)

        S.WIP += WOP_d_com + SOP_d_com * 0.75 + SIP_d_com
        S.WOP += SOP_d_com * 0.25
        S.NH4 += SON_d_com

        S.DP_sum += SIP_ASIM + WOP_ASIM + SOP_ASIM + WIP_ASIM
        S.N_sum += SON_ASIM + NH4_ASIM

        S.manure_mass = max(0.0, S.manure_mass - d_com - man_ASIM)

        S.manure_cov = S.manure_cov - cov_d_com - cov_ASIM

        # TODO should be commented out
        # S.manure_cov = S.cover_SLP * S.manure_mass * S.area

        # convert soil P form KG/HA to KG and add manure P decomposed

        S.listOfSoilLayers[0].active_P += SIP_ASIM * 0.6

        # TODO math
        S.listOfSoilLayers[0].labile_P += 0.6 * (WIP_ASIM + WOP_ASIM + SOP_ASIM)

        if S.listOfSoilLayers[1].bottom_depth_cm <= 15.0:

            S.listOfSoilLayers[1].active_P += SIP_ASIM * 0.3
            S.listOfSoilLayers[2].active_P += SIP_ASIM * 0.1

            # TODO math
            S.listOfSoilLayers[1].labile_P += 0.3 * (WIP_ASIM + WOP_ASIM + SOP_ASIM)
            S.listOfSoilLayers[2].labile_P += 0.1 * (WIP_ASIM + WOP_ASIM + SOP_ASIM)

        else:

            S.listOfSoilLayers[1].active_P += SIP_ASIM * 0.4

            # TODO math
            S.listOfSoilLayers[1].labile_P += 0.4 * (WIP_ASIM + WOP_ASIM + SOP_ASIM)

    # convert soil P from KG/HA to KG and add manure P decomposed

    for w in range(0, 3):
        S.listOfSoilLayers[w].active_P /= S.area
        S.listOfSoilLayers[w].labile_P /= S.area

    # calculate runoff P in MG/L from both soil and manure
    # and manure P in runoff from spreading and grazing

    if runoff > 0.0:
        S.soil_P[0] = S.listOfSoilLayers[0].labile_P / S.listOfSoilLayers[0].bulkDensity / S.thickness_cm[0] / 0.1
        S.SRP_MGL = S.soil_P[0] * 0.005

        S.T_runoff_IP = S.runoff_IP + S.SRP_MGL + S.fert_runoff_P

    else:
        S.SRP_MGL = 0.0
        S.T_runoff_IP = 0.0
