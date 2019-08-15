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

# calculates TP, WIP, and WOP added in the manure, adds P to surface manure
# pools. All units are KG or HA


def update_all(S, time):

    day = time.day
    year = time.year
    m_app = S.manure
    mass = m_app.mass

    for i in range(0, len(m_app.day)):
        if m_app.day[i] == day and m_app.year[i] - S.start_year + 1 == year:

            S.manure_type = m_app.type[i]

            # S.cover_SLP = 0.0154 * mass[i] ** -0.555

            # m_app.percent_cover[i] = min(1.0, 0.012 * mass[i] ** 0.48)

            cover_app = m_app.percent_cover[i] * S.area
            P_app = mass[i] * m_app.P_frac[i]
            N_app = mass[i] * m_app.N_frac[i]
            S.manure_sum += mass[i]
            S.manure_P_sum += P_app
            S.manure_N_sum += N_app

            S.moisture = (S.moisture * S.manure_mass + (1.0 - m_app.dry_matter[i]) * mass[i]) \
                         / (S.manure_mass + mass[i])
            wet_rate = mass[i] / m_app.dry_matter[i] / cover_app
            infiltration = min(0.9, 0.000002 * wet_rate + 0.267)

            for w in range(0, 3):
                S.soil_layers[w].active_P *= S.area
                S.soil_layers[w].labile_P *= S.area

            # surface application

            if m_app.depth[i] == 0.0:

                # infiltrate manure P if less than 15% solids

                if m_app.dry_matter[i] <= 0.15:
                    S.manure_cov = min(S.area, S.manure_cov + cover_app * 0.5)
                    S.manure_mass += mass[i] * 0.8
                    S.WIP += P_app * m_app.WIP_frac[i] * infiltration
                    S.WOP += P_app * m_app.WOP_frac[i] * infiltration
                    S.SOP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.75 * infiltration
                    S.SIP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.25 * infiltration
                    S.NH4 += N_app * m_app.N_frac[i] * infiltration * 0.65
                    S.SON += N_app * (1.0 - m_app.N_frac[i]) * infiltration

                    # add manure P infiltrated into soil

                    # TODO these two lines are not included in the else below (111) but in the next (68)
                    S.soil_layers[0].active_P += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.25 * (1.0 - infiltration)
                    S.soil_layers[0].labile_P += P_app * m_app.WIP_frac[i] * (1.0 - infiltration) + P_app \
                                           * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.75 * 0.95 * (1.0 - infiltration) + P_app * m_app.WOP_frac[i] \
                                           * 0.95 * (1.0 - infiltration)

                else:
                    S.manure_cov = min(S.area, S.manure_cov + cover_app)
                    S.manure_mass += mass[i]
                    S.WIP += P_app * m_app.WIP_frac[i]
                    S.WOP += P_app * m_app.WOP_frac[i]
                    S.SOP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.75
                    S.SIP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.25
                    S.NH4 += N_app * m_app.N_frac * 0.65
                    S.SON += N_app * (1.0 - m_app.N_frac)

            else:

                # subsurface application
                # infiltrate manure P if less than 15% solids

                if m_app.dry_matter[i] <= 0.15:

                    S.manure_cov = min(S.area, S.manure_cov + cover_app
                                       * m_app.surface_percent[i] * 0.5)
                    S.manure_mass += mass[i] * m_app.surface_percent[i] * 0.8
                    S.WIP += P_app * m_app.WIP_frac[i] * infiltration * m_app.surface_percent[i]
                    S.WOP += P_app * m_app.WOP_frac[i] * infiltration * m_app.surface_percent[i]
                    S.SOP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                             * 0.25 * infiltration * m_app.surface_percent[i]
                    S.SIP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                             * 0.75 * infiltration * m_app.surface_percent[i]
                    S.NH4 += N_app * m_app.N_frac * 0.65 * infiltration \
                                    * m_app.surface_percent[i]
                    S.SON += N_app * (1.0 - m_app.N_frac) * infiltration \
                                    * m_app.surface_percent[i]

                    # add manure P infiltrated into soil

                    S.soil_layers[0].active_P += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.25 * (1.0 - infiltration) \
                                           * (1.0 - m_app.surface_percent[i])
                    S.soil_layers[0].labile_P += P_app * m_app.WIP_frac[i] * (1.0 - infiltration) \
                                           * (1.0 - m_app.surface_percent[i]) + P_app \
                                           * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.75 * 0.95 * (1.0 - infiltration) \
                                           * (1.0 - m_app.surface_percent[i]) + P_app * m_app.WOP_frac[i] \
                                           * 0.95 * (1.0 - infiltration) * (1.0 - m_app.surface_percent[i])

                else:
                    S.manure_cov = min(S.area, S.manure_cov + cover_app
                                       * m_app.surface_percent[i])
                    S.manure_mass += mass[i] * m_app.surface_percent[i]
                    S.WIP += P_app * m_app.WIP_frac[i] * m_app.surface_percent[i]
                    S.WOP += P_app * m_app.WOP_frac[i] * m_app.surface_percent[i]
                    S.SOP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.75 \
                             * m_app.surface_percent[i]
                    S.SIP += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.25 \
                             * m_app.surface_percent[i]
                    S.NH4 += N_app * m_app.N_frac * 0.65 * m_app.surface_percent[i]
                    S.SON += N_app * (1.0 - m_app.N_frac) * m_app.surface_percent[i]

                    S.soil_layers[0].active_P += P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.25 * (1.0 - m_app.surface_percent[i])
                    S.soil_layers[0].labile_P += P_app * m_app.WIP_frac[i] * (1.0 - m_app.surface_percent[i]) \
                                           + P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) \
                                           * 0.75 * 0.95 * (1.0 - m_app.surface_percent[i]) + P_app \
                                           * m_app.WOP_frac[i] * 0.95 * (1.0 - m_app.surface_percent[i])

                no = 0
                for n in range(0, 3):
                    if S.soil_layers[n].bottom_depth_cm >= m_app.depth[i]:
                        break
                    no += 1

                sum_fact = 0.0

                for k in range(0, no):
                    fact = S.soil_layers[k].bottom_depth_cm / m_app.depth[i]

                    S.soil_layers[k].labile_P += P_app * m_app.WIP_frac[i] * (1.0 - m_app.surface_percent[i]) \
                                           * fact + P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.75 \
                                           * 0.95 * (1.0 - infiltration) * (1.0 - m_app.surface_percent[i]) \
                                           * fact + P_app * m_app.WOP_frac[i] * 0.95 * (1.0 - infiltration) \
                                           * (1.0 - m_app.surface_percent[i]) * fact
                    S.soil_layers[k].active_P += P_app * fact * (1.0 - (m_app.WIP_frac[i]
                                                                             + m_app.WOP_frac[i])) * 0.25 \
                                                      * (1.0 - m_app.surface_percent[i])

                    sum_fact += fact

                fact = 1.0 - sum_fact

                S.soil_layers[no].labile_P += P_app * m_app.WIP_frac[i] * (1.0 - m_app.surface_percent[1]) \
                                       * fact + P_app * (1.0 - (m_app.WIP_frac[i] + m_app.WOP_frac[i])) * 0.75 \
                                       * 0.95 * (1.0 - infiltration) * (1.0 - m_app.surface_percent[i]) \
                                       * fact + P_app * m_app.WOP_frac[i] * 0.95 * (1.0 - infiltration) \
                                       * (1.0 - m_app.surface_percent[i]) * fact
                S.soil_layers[no].active_P += P_app * fact * (1.0 - (m_app.WIP_frac[i]
                                                                         + m_app.WOP_frac[i])) * 0.25 \
                                                  * (1.0 - m_app.surface_percent[i])

            for w in range(0, 3):
                S.soil_layers[w].active_P /= S.area
                S.soil_layers[w].labile_P /= S.area

            S.manure_mass_app = S.manure_mass

    cow_mass_app = S.cows[year][day - 1] * 8.9 + S.heifer[year][day - 1] * 3.7 \
                   + S.dry_cow[year][day - 1] * 4.9 + S.d_calf[year][day - 1] * 1.4 \
                   + S.beef_cow[year][day - 1] * 6.6 + S.b_calf[year][day - 1] * 2.7

    if cow_mass_app > 0.0:

        S.moisture = (S.moisture * S.manure_mass + 0.9 * cow_mass_app) \
                     / (S.manure_mass + cow_mass_app)

        S.manure_mass += cow_mass_app
        S.manure_cov += cow_mass_app / 0.25 * 659.0 / 100 ** 4

        cow_P_app = S.cows[year][day - 1] * 8.9 * 0.0088 + S.heifer[year][day - 1] * 3.7 \
                    * 0.0054 + S.dry_cow[year][day - 1] * 4.9 * 0.0061 \
                    + S.d_calf[year][day - 1] * 1.4 * 0.0054 + S.beef_cow[year][day - 1] \
                    * 6.6 * 0.0067 + S.b_calf[year][day - 1] * 2.7 * 0.0092

        S.WIP += cow_P_app * 0.50
        S.WOP += cow_P_app * 0.05
        S.SOP += cow_P_app * 0.45 * 0.75
        S.SIP += cow_P_app * 0.45 * 0.25

        # update cumulative manure and TP added during model run

        S.manure_sum += cow_mass_app
        S.manure_P_sum += cow_P_app

        S.manure_mass_app = S.manure_mass
