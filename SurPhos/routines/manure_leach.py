
# this subroutine estimates P leaching from surface manure with rainfall
# and P infiltration into soil and loss in runoff

from math import exp


def update_all(S, weather, time):

    day = time.day
    year = time.year

    rainfall = weather.rainfall
    runoff = weather.runoff
    temp = weather.temp
    m_app = S.manure_app

    TFA = max(0.0, ((2.0 * 32.0 ** 2 * temp[year][day - 1] ** 2
                    - temp[year][day - 1] ** 4)) / 32.0 ** 4)

    for w in range(0, 3):
        S.active_P_layer[w] *= S.area
        S.labile_P_layer[w] *= S.area

    # P leached from manure on surface to rain and runoff water in KG

    if S.manure_mass > 0.0 and S.manure_cov > 0.0:
        water_manure = rainfall[year][day - 1] / S.manure_mass \
                       * S.manure_cov * 10000.0

        if rainfall[year][day - 1] > 0.0:

            if S.manure_type == 1:
                manure_extr = min(1.0, 1.2 * water_manure / (water_manure + 73.1))
                # manure_extr = min(1.0, 0.0000144 * water_manure ** 2.0285)
                NH_extr = min(1.0, 0.9 * water_manure / (water_manure + 7.1))
            else:
                manure_extr = min(1.0, 2.2 * water_manure / (water_manure + 300.1))
                NH_extr = 0.0  # TODO I added this, otherwise it may not be initialized

        else:
            manure_extr = 0.0
            NH_extr = 0.0

        MIP_leach = max(0.0, manure_extr * S.WIP)
        MOP_leach = max(0.0, manure_extr * S.WOP / 0.6)
        MNH_leach = max(0.0, NH_extr * S.manure_NH4)

        if MIP_leach > S.WIP:
            MIP_leach = S.WIP
        if MOP_leach > S.WOP:
            MOP_leach = S.WOP
        if MNH_leach > S.manure_NH4:
            MOP_leach = S.manure_NH4

        S.WIP = max(0.0, S.WIP - MIP_leach)
        S.WOP = max(0.0, S.WOP - MOP_leach)
        S.manure_NH4 = max(0.0, S.manure_NH4 - MNH_leach)

        S.TIP_leach += MIP_leach
        S.TOP_leach += MOP_leach
        S.TN_leach += MNH_leach

        # calculates the concentration of all dissolved P in runoff in MG/L

        if runoff[year][day - 1] > 0.0:

            S.PD_factor = (runoff[year][day - 1] / rainfall[year][day - 1]) ** 0.225
            S.ND_factor = runoff[year][day - 1] / rainfall[year][day - 1]
            # S.ND_factor = 0.034 * exp((runoff[year][day - 1] / rainfall[year][day - 1]) * 3.4)

            S.runoff_IP = MIP_leach / (rainfall[year][day - 1] / 10.0) / S.area * 10.0 * S.PD_factor
            S.runoff_OP = MOP_leach / (rainfall[year][day - 1] / 10.0) / S.area * 10.0 * S.PD_factor
            S.runoff_NH = MNH_leach / (rainfall[year][day - 1] / 10.0) / S.area * 10.0 * S.ND_factor

            # calculate manure runoff P in KG

            runoff_MIP = S.runoff_IP * runoff[year][day - 1] * 0.01 * S.area
            runoff_MOP = S.runoff_OP * runoff[year][day - 1] * 0.01 * S.area
            runoff_MNH = S.runoff_NH * runoff[year][day - 1] * 0.01 * S.area

            if runoff_MIP < 0.0:
                runoff_MIP = 0.0
            if runoff_MOP < 0.0:
                runoff_MOP = 0.0
            if runoff_MNH < 0.0:
                runoff_MNH = 0.0

            if runoff_MIP > MIP_leach:
                runoff_MIP = MIP_leach
            if runoff_MOP > MOP_leach:
                runoff_MOP = MOP_leach
            if runoff_MNH > MNH_leach:
                runoff_MNH = MNH_leach

        else:
            runoff_MIP = 0.0
            runoff_MOP = 0.0
            runoff_MNH = 0.0
            S.runoff_IP = 0.0
            S.runoff_OP = 0.0
            S.runoff_NH = 0.0

        # convert soil P from KG/HA to KG and add manure P leached

        S.labile_P_layer[0] += (MIP_leach - runoff_MIP) * 0.6
        S.labile_P_layer[0] += (MOP_leach - runoff_MOP) * 0.6

        if S.depths_layer[1] <= 15.0:
            S.labile_P_layer[1] += (MIP_leach - runoff_MIP) * 0.3
            S.labile_P_layer[1] += (MOP_leach - runoff_MOP) * 0.3
            S.labile_P_layer[2] += (MIP_leach - runoff_MIP) * 0.1
            S.labile_P_layer[2] += (MOP_leach - runoff_MOP) * 0.1
        else:
            S.labile_P_layer[1] += (MIP_leach - runoff_MIP) * 0.4
            S.labile_P_layer[1] += (MOP_leach - runoff_MOP) * 0.4

        # add manure P leached and in runoff to running total

        S.WIP_R_sum += runoff_MIP
        S.WOP_R_sum += runoff_MOP
        S.NH_R_sum += S.runoff_NH
        S.WIP_L_sum += (MIP_leach - runoff_MIP)
        S.WOP_L_sum += (MOP_leach - runoff_MOP)
        S.NH_L_sum += (MNH_leach - runoff_MNH)

        # decompose manure and manure P in KG

        wet = -0.3 * S.moisture + 0.27
        dry = (-0.05 * (S.manure_mass / S.manure_mass_app) + 0.075) * TFA

        if rainfall[year][day - 1] > 4.0:
            S.moisture += wet
        elif rainfall[year][day - 1] > 1.0:
            S.moisture = S.moisture  # TODO whyyyyyy
        else:
            S.moisture -= dry

        if S.moisture > 0.9:
            S.moisture = 0.9
        if S.moisture < 0.0:
            S.moisture = 0.0

        AWDCR = 0.003 * TFA ** 0.5
        ASIM = 30.0 * exp(2.5 * S.moisture)

        d_com = max(0.0, S.manure_mass * AWDCR)
        if d_com > S.manure_mass:
            d_com = S.manure_mass
        cov_d_com = max(0.0, d_com / S.manure_mass * S.manure_cov)
        if cov_d_com > S.manure_cov:
            cov_d_com = S.manure_cov

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
        if SIP_d_com > S.SIP:
            SIP_d_com = S.SIP
        SOP_d_com = max(0.0, S.SOP * 0.01 * min(TFA, S.moisture))
        if SOP_d_com > S.SOP:
            SOP_d_com = S.SOP
        SON_d_com = max(0.0, S.manure_SON * 0.01 * min(TFA, S.moisture))
        if SON_d_com > S.manure_SON:
            SON_d_com = S.manure_SON
        WOP_d_com = max(0.0, S.WOP * 0.1 * min(TFA, S.moisture))
        if WOP_d_com > S.WOP:
            WOP_d_com = S.WOP
        man_ASIM = max(0.0, ASIM * TFA * S.manure_cov)
        if man_ASIM > S.manure_mass:
            man_ASIM = S.manure_mass
        cov_ASIM = max(0.0, man_ASIM / S.manure_mass * S.manure_cov)
        # if cov_d_com > S.manure_cov:  # TODO seems like an error, why is it cov_d_com
        #     cov_ASIM = S.manure_cov
        if cov_ASIM > S.manure_cov:  # TODO fixed version of above
            cov_ASIM = S.manure_cov
        WIP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.WIP)
        if WIP_ASIM > S.WIP:
            WIP_ASIM = S.WIP
        NH_ASIM = max(0.0, man_ASIM / S.manure_mass * S.manure_NH4)
        if NH_ASIM > S.manure_NH4:
            NH_ASIM = S.manure_NH4
        SIP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.SIP)
        if SIP_ASIM > S.SIP:
            SIP_ASIM = S.SIP
        WOP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.WOP)
        if WOP_ASIM > S.WOP:
            WOP_ASIM = S.WOP
        SOP_ASIM = max(0.0, man_ASIM / S.manure_mass * S.SOP)
        if SOP_ASIM > S.SOP:
            SOP_ASIM = S.SOP
        SON_ASIM = max(0.0, man_ASIM / S.manure_mass * S.manure_SON)
        if SON_ASIM > S.manure_SON:
            SON_ASIM = S.manure_SON

        S.SOP = max(0.0, S.SOP - SOP_ASIM - SOP_d_com)
        S.SON = max(0.0, S.manure_SON - SON_ASIM - SON_d_com)
        S.WOP = max(0.0, S.WOP - WOP_ASIM - WOP_d_com)
        S.SIP = max(0.0, S.SIP - SIP_ASIM - SIP_d_com)
        S.WIP = max(0.0, S.WIP - WIP_ASIM)
        S.manure_NH4 = max(0.0, S.manure_NH4 - NH_ASIM)

        S.WIP += WOP_d_com + SOP_d_com * 0.75 + SIP_d_com
        S.WOP += SOP_d_com * 0.25
        S.manure_NH4 += SON_d_com

        S.DP_sum += SIP_ASIM + WOP_ASIM + SOP_ASIM + WIP_ASIM
        S.N_sum += SON_ASIM + NH_ASIM

        S.manure_mass = max(0.0, S.manure_mass - d_com - man_ASIM)

        S.manure_cov = S.manure_cov - cov_d_com - cov_ASIM

        # TODO should be commented out
        # S.manure_cov = S.cover_SLP * S.manure_mass * S.area

        # convert soil P form KG/HA to KG and add manure P decomposed

        S.active_P_layer[0] += SIP_ASIM * 0.6
        S.labile_P_layer[0] += WIP_ASIM * 0.6
        S.labile_P_layer[0] += WOP_ASIM * 0.6
        S.labile_P_layer[0] += SOP_ASIM * 0.6

        if S.depths_layer[1] <= 15.0:

            S.active_P_layer[1] += SIP_ASIM * 0.3
            S.active_P_layer[2] += SIP_ASIM * 0.1

            S.labile_P_layer[1] += WIP_ASIM * 0.3
            S.labile_P_layer[2] += WIP_ASIM * 0.1

            S.labile_P_layer[1] += WOP_ASIM * 0.3
            S.labile_P_layer[2] += WOP_ASIM * 0.1

            S.labile_P_layer[1] += SOP_ASIM * 0.3
            S.labile_P_layer[2] += SOP_ASIM * 0.1

        else:

            S.active_P_layer[1] += SIP_ASIM * 0.4
            S.labile_P_layer[1] += WIP_ASIM * 0.4
            S.labile_P_layer[1] += WOP_ASIM * 0.4
            S.labile_P_layer[1] += SOP_ASIM * 0.4

    else:
        water_manure = 0.0

    # convert soil P from KG/HA to KG and add manure P decomposed

    for w in range(0, 3):
        S.active_P_layer[w] /= S.area
        S.labile_P_layer[w] /= S.area

    # calculate runoff P in MG/L from both soil and manure
    # and manure P in runoff from spreading and grazing

    if runoff[year][day - 1] > 0.0:
        S.soil_P[0] = S.labile_P_layer[0] / S.bulk_density_layer[0] / S.thick_layer[0] / 0.1
        S.SRP_MGL = S.soil_P[0] * 0.005

        S.T_runoff_IP = S.runoff_IP + S.SRP_MGL + S.fert_runoff_P

    else:
        S.SRP_MGL = 0.0
        S.T_runoff_IP = 0.0

