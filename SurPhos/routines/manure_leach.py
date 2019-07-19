
# this subroutine estimates P leaching from surface manure with rainfall
# and P infiltration into soil and loss in runoff

from math import exp


def update_all(surphos, weather, time):

    day = time.day
    year = time.year

    rainfall = weather.rainfall
    runoff = weather.runoff
    temp = weather.temp
    m_app = surphos.manure_app

    runoff_IP = 0.0
    runoff_OP = 0.0
    runoff_NH = 0.0

    TFA = max(0.0, (2.0 * 32.0 ** 2 * temp[year][day - 1] ** 2
                    - temp[year][day - 1] ** 4) / 32.0 ** 4)

    for w in range(0, 3):
        surphos.active_P_layer[w] *= surphos.area
        surphos.labile_P_layer[w] *= surphos.area

    # P leached from manure on surface to rain and runoff water in KG

    if surphos.manure_mass > 0.0 and surphos.manure_cov > 0.0:
        water_manure = rainfall[year][day - 1] / surphos.manure_mass \
                       * surphos.manure_cov * 10000.0

        if rainfall[year][day - 1] > 0.0:

            if m_app.type == 1:
                manure_extr = min(1.0, 1.2 * water_manure / (water_manure + 73.1))
                manure_extr = min(1.0, 0.0000144 * water_manure ** 2.0285)  # TODO uhhhh redundant
                NH_extr = min(1.0, 0.9 * water_manure / (water_manure + 7.1))
            else:
                manure_extr = min(1.0, 2.2 * water_manure / (water_manure + 300.1))
                NH_extr = 0.0  # TODO I added this, otherwise it may not be initialized

        else:
            manure_extr = 0.0
            NH_extr = 0.0

        MIP_leach = max(0.0, manure_extr * surphos.WIP)
        MOP_leach = max(0.0, manure_extr * surphos.WOP / 0.6)
        MNH_leach = max(0.0, NH_extr * surphos.manure_NH4)

        if MIP_leach > surphos.WIP:
            MIP_leach = surphos.WIP
        if MOP_leach > surphos.WOP:
            MOP_leach = surphos.WOP
        if MNH_leach > surphos.manure_NH4:
            MOP_leach = surphos.manure_NH4

        surphos.WIP = max(0.0, surphos.WIP - MIP_leach)
        surphos.WOP = max(0.0, surphos.WOP - MOP_leach)
        surphos.manure_NH4 = max(0.0, surphos.manure_NH4 - MNH_leach)

        surphos.TIP_leach += MIP_leach
        surphos.TOP_leach += MOP_leach
        surphos.TN_leach += MNH_leach

        # calculates the concentration of all dissolved P in runoff in MG/L

        if runoff[year][day - 1] > 0.0:

            surphos.PD_factor = (runoff[year][day - 1] / rainfall[year][day - 1]) ** 0.225
            surphos.ND_factor = runoff[year][day - 1] / rainfall[year][day - 1]
            surphos.ND_factor = 0.034 * exp((runoff[year][day - 1] / rainfall[year][day - 1]) * 3.4)

            runoff_IP = MIP_leach / (rainfall[year][day - 1] / 10.0) / surphos.area * 10.0 * surphos.PD_factor
            runoff_OP = MOP_leach / (rainfall[year][day - 1] / 10.0) / surphos.area * 10.0 * surphos.PD_factor
            runoff_NH = MNH_leach / (rainfall[year][day - 1] / 10.0) / surphos.area * 10.0 * surphos.PD_factor

            # calculate manure runoff P in KG

            runoff_MIP = runoff_IP * runoff[year][day - 1] * 0.01 * surphos.area
            runoff_MOP = runoff_OP * runoff[year][day - 1] * 0.01 * surphos.area
            runoff_MNH = runoff_NH * runoff[year][day - 1] * 0.01 * surphos.area

            if runoff_MIP < 0.0:
                runoff_MIP = 0.0
            if runoff_MOP < 0.0:
                runoff_MOP = 0.0
            if runoff_MNH < 0.0:
                runoff_MNH = 0.0

            if runoff_MIP > MIP_leach:
                runoff_MIP = MIP_leach
            if runoff_MOP > MOP_leach:
                runoff_MOP = MIP_leach
            if runoff_MNH > MNH_leach:
                runoff_MNH = MNH_leach

        else:
            runoff_MIP = 0.0
            runoff_MOP = 0.0
            runoff_MNH = 0.0
            runoff_IP = 0.0
            runoff_OP = 0.0
            runoff_NH = 0.0

        # convert soil P from KG/HA to KG and add manure P leached

        surphos.labile_P_layer[0] += (MIP_leach - runoff_MIP) * 0.6
        surphos.labile_P_layer[0] += (MOP_leach - runoff_MOP) * 0.6

        if surphos.depths_layer[1] <= 15.0:
            surphos.labile_P_layer[1] += MIP_leach - runoff_MIP * 0.3
            surphos.labile_P_layer[1] += MOP_leach - runoff_MOP * 0.3
            surphos.labile_P_layer[2] += MIP_leach - runoff_MIP * 0.1
            surphos.labile_P_layer[2] += MOP_leach - runoff_MOP * 0.1
        else:
            surphos.labile_P_layer[1] += MIP_leach - runoff_MIP * 0.4
            surphos.labile_P_layer[1] += MOP_leach - runoff_MOP * 0.4

        # add manure P leached and in runoff to running total

        surphos.WIP_R_sum += runoff_MIP
        surphos.WOP_R_sum += runoff_MOP
        surphos.NH_R_sum += runoff_NH
        surphos.WIP_L_sum += MIP_leach - runoff_MIP
        surphos.WOP_L_sum += MOP_leach - runoff_MOP
        surphos.NH_L_sum += MNH_leach - runoff_MNH

        # decompose manure and manure P in KG

        wet = -0.3 * surphos.moisture + 0.27
        dry = (-0.05 * surphos.manure_mass / surphos.manure_mass_app + 0.075) * TFA

        if rainfall[year][day - 1] > 4.0:
            surphos.moisture += wet
        elif rainfall[year][day - 1] > 1.0:
            surphos.moisture = surphos.moisture  # TODO whyyyyyy
        else:
            surphos.moisture -= dry

        if surphos.moisture > 0.9:
            surphos.moisture = 0.9
        if surphos.moisture < 0.0:
            surphos.moisture = 0.0

        AWDCR = 0.003 * TFA ** 0.5
        ASIM = 30.0 * exp(2.5 * surphos.moisture)

        d_com = max(0.0, surphos.manure_mass * AWDCR)
        if d_com > surphos.manure_mass:
            d_com = surphos.manure_mass
        cov_d_com = max(0.0, d_com / surphos.manure_mass * surphos.manure_cov)
        if cov_d_com > surphos.manure_cov:
            cov_d_com = surphos.manure_cov

        # TODO should be commented out
        # SIP_d_com = max(0.0, surphos.SIP * 0.0025 * TFA * surphos.moisture)
        # if SIP_d_com > surphos.SIP:
        #     SIP_d_com = surphos.SIP
        # SOP_d_com = max(0.0, surphos.SOP * 0.01 * TFA * surphos.moisture)
        # if SOP_d_com > surphos.SOP:
        #     SOP_d_com = surphos.SOP
        # man_ASIM = max(0.0, surphos.manure_mass * 0.025 * TFA * surphos.moisture)
        # if man_ASIM > surphos.manure_mass:
        #     man_ASIM = surphos.manure_mass

        SIP_d_com = max(0.0, surphos.SIP * 0.0025 * min(TFA, surphos.moisture))
        if SIP_d_com > surphos.SIP:
            SIP_d_com = surphos.SIP
        SOP_d_com = max(0.0, surphos.SOP * 0.01 * min(TFA, surphos.moisture))
        if SOP_d_com > surphos.SOP:
            SOP_d_com = surphos.SOP
        SON_d_com = max(0.0, surphos.manure_SON * 0.01 * min(TFA, surphos.moisture))
        if SON_d_com > surphos.manure_SON:
            SON_d_com = surphos.manure_SON
        WOP_d_com = max(0.0, surphos.WOP * 0.1 * min(TFA, surphos.moisture))
        if WOP_d_com > surphos.WOP:
            WOP_d_com = surphos.WOP
        man_ASIM = max(0.0, ASIM * TFA * surphos.manure_cov)
        if man_ASIM > surphos.manure_mass:
            man_ASIM = surphos.manure_mass
        cov_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.manure_cov)
        if cov_d_com > surphos.manure_cov:  # TODO seems like an error, why is it cov_d_com
            cov_ASIM = surphos.manure_cov
        WIP_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.WIP)
        if WIP_ASIM > surphos.WIP:
            WIP_ASIM = surphos.WIP
        NH_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.manure_NH4)
        if NH_ASIM > surphos.manure_NH4:
            NH_ASIM = surphos.manure_NH4
        SIP_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.SIP)
        if SIP_ASIM > surphos.SIP:
            SIP_ASIM = surphos.SIP
        WOP_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.WOP)
        if WOP_ASIM > surphos.WOP:
            WOP_ASIM = surphos.WOP
        SOP_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.SOP)
        if SOP_ASIM > surphos.SOP:
            SOP_ASIM = surphos.SOP
        SON_ASIM = max(0.0, man_ASIM / surphos.manure_mass * surphos.manure_SON)
        if SON_ASIM > surphos.manure_SON:
            SON_ASIM = surphos.manure_SON

        surphos.SOP = max(0.0, surphos.SOP - SOP_ASIM - SOP_d_com)
        surphos.SON = max(0.0, surphos.manure_SON - SON_ASIM - SON_d_com)
        surphos.WOP = max(0.0, surphos.WOP - WOP_ASIM - WOP_d_com)
        surphos.SIP = max(0.0, surphos.SIP - SIP_ASIM - SIP_d_com)
        surphos.WIP - max(0.0, surphos.WIP - WIP_ASIM)
        surphos.manure_NH4 = max(0.0, surphos.manure_NH4 - NH_ASIM)

        surphos.WIP += WOP_d_com + SOP_d_com * 0.75 + SIP_d_com
        surphos.WOP += SOP_d_com * 0.25
        surphos.manure_NH4 += SON_d_com

        surphos.DP_sum += SIP_ASIM + WOP_ASIM + SOP_ASIM + WIP_ASIM
        surphos.N_sum += SON_ASIM + NH_ASIM

        surphos.manure_mass = max(0.0, surphos.manure_mass - d_com - ASIM)
        surphos.manure_cov -= cov_d_com - cov_ASIM

        # TODO should be commented out
        # surphos.manure_cov = surphos.cover_SLP * surphos.manure_mass * surphos.area

        # convert soil P form KG/HA to KG and add manure P decomposed

        surphos.active_P_layer[0] += SIP_ASIM * 0.6
        surphos.labile_P_layer[0] += WIP_ASIM * 0.6
        surphos.labile_P_layer[0] += WOP_ASIM * 0.6
        surphos.labile_P_layer[0] += SOP_ASIM * 0.6

        if surphos.depths_layer[1] <= 15.0:

            surphos.active_P_layer[1] += SIP_ASIM * 0.3
            surphos.active_P_layer[2] += SIP_ASIM * 0.1

            surphos.labile_P_layer[1] += WIP_ASIM * 0.3
            surphos.labile_P_layer[2] += WIP_ASIM * 0.1

            surphos.labile_P_layer[1] += WOP_ASIM * 0.3
            surphos.labile_P_layer[2] += WOP_ASIM * 0.1

            surphos.labile_P_layer[1] += SOP_ASIM * 0.3
            surphos.labile_P_layer[2] += SOP_ASIM * 0.1

        else:

            surphos.active_P_layer[1] += SIP_ASIM * 0.4
            surphos.labile_P_layer[1] += WIP_ASIM * 0.4
            surphos.labile_P_layer[1] += WOP_ASIM * 0.4
            surphos.labile_P_layer[1] += SOP_ASIM * 0.4

    else:
        water_manure = 0.0

        # convert soil P from KG/HA to KG and add manure P decomposed

        for w in range(0, 3):
            surphos.active_P_layer[w] /= surphos.area
            surphos.labile_P_layer[w] /= surphos.area

        # calculate runoff P in MG/L from both soil and manure
        # and manure P in runoff from spreading and grazing

        if runoff[year][day - 1] > 0.0:
            surphos.soil_P[0] = surphos.labile_P_layer[0] / surphos.bulk_density_layer[0] / surphos.thick_layer[0] / 0.1
            surphos.SRP_MGL = surphos.soil_P[0] * 0.005

            surphos.T_runoff_IP = runoff_IP + surphos.SRP_MGL + surphos.fert_runoff_P

        else:
            surphos.SRP_MGL = 0.0
            surphos.T_runoff_IP = 0.0

