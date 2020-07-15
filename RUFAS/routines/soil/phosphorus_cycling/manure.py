################################################################################
"""
SurPhos
File name: manure.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################


# calculates # of plops added per day and amount of TP, WIP, and WOP added
# in manure, adds P to surface manure pools, and updates cumulative manure
# and TP added during model run
# "pseudocode_soil" S.5.C
def update_all(S, time):

    day = time.day
    year = time.year
    m_app = S.manure
    mass = m_app.mass
    S.manure_P = 0.0
    S.manure_app = 0.0

    for i in range(0, len(m_app.day)):
        if m_app.day[i] == day and m_app.year[i] - S.start_year + 1 == year:

            S.manure_type = m_app.type[i]

            # Update manure characteristics
            # S.5.C.I.1-6
            cover_app = m_app.percent_cover[i] * S.area
            P_app = mass[i] * m_app.P_frac[i]
            S.manure_app = mass[i]
            S.manure_P = P_app

            S.manure_moisture = (S.manure_moisture * S.manure_mass + (1.0 - m_app.DM[i]) * mass[i]) \
                         / (S.manure_mass + mass[i])
            wet_rate = mass[i] / m_app.DM[i] / cover_app
            infiltration = min(0.9, 0.000002 * wet_rate + 0.267)

            # S.5.B.3
            for layer in S.soil_layers:
                layer.active_P *= S.area
                layer.labile_P *= S.area

            # application factors
            # S.5.C.II.1
            I_fac = 1.0 - infiltration
            S_fac = 1.0 - m_app.surface_percent[i]
            W_fac = 1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])

            # concentration factors
            # S.5.C.II.2
            C_WIP = P_app * m_app.WIP_frac[i] * I_fac
            C_WOP = P_app * m_app.WOP_frac[i] * 0.95 * I_fac

            # slurry factors
            # S.5.C.II.3
            S_fac_cover = 1.0
            S_fac_mass = 1.0
            if m_app.DM[i] <= 0.15:
                S_fac_cover = 0.5
                S_fac_mass = 0.8
                S_fac = infiltration

            # depth factors
            # S.5.C.II.4
            D_fac_1 = 1.0
            D_fac_2 = 1.0
            if m_app.depth[i] > 0.0:
                D_fac_1 = S_fac * C_WIP * C_WOP
                D_fac_2 = S_fac

            # update manure features and composition
            # S.5.C.II.5
            S.manure_cov = min(S.area, S.manure_cov + cover_app * S_fac_cover)
            S.manure_mass += mass[i] * S_fac_mass
            S.WIP += P_app * m_app.WIP_frac[i] * S_fac
            S.WOP += P_app * m_app.WOP_frac[i] * S_fac
            S.SOP += P_app * W_fac * 0.75 * m_app.surface_percent[i] * S_fac
            S.SIP += P_app * W_fac * 0.25 * m_app.surface_percent[i] * S_fac

            # update active and labile soil pools for each layer affected by the application
            # S.5.C.II.6
            last_layer = 0
            D_fac_sum = 0
            for layer in S.soil_layers:
                if layer.bottom_depth_cm < m_app.depth[i]:
                    D_fac = layer.bottom_depth_cm / m_app.depth[i]
                    layer.active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
                    layer.labile_P += C_WIP + C_WOP + (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

                    D_fac_sum += D_fac
                    last_layer += 1

            D_fac = 1 - D_fac_sum
            S.soil_layers[last_layer].active_P += P_app * W_fac * 0.25 * I_fac * D_fac_1 * D_fac
            S.soil_layers[last_layer].labile_P += C_WIP + C_WOP + \
                                                  (P_app * W_fac * 0.75 * 0.95 * I_fac * D_fac_2) * D_fac

            # S.5.B.4
            for layer in S.soil_layers:
                layer.active_P /= S.area
                layer.labile_P /= S.area

            S.manure_mass_app = S.manure_mass
