################################################################################
"""
SurPhos
File name: fertilizer.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           WIlliam Donovan, wmdonovan@wisc.edu
"""
################################################################################

# calculates P added in fertilizer, adds fertilizer P to surface pool,
# and updates cumulative fertilizer P added during model run

# calculates TP, WIP, and WOP added in manure, adds to surface manure
# pools. All units are KG or HA


def update_all(S, time):

    day = time.day
    year = time.year
    fert_app = S.fertilizer

    for i in range(len(fert_app.day)):
        if fert_app.day[i] == day and fert_app.year[i] - S.start_year + 1 == year:
            S.fert_applied_sum += fert_app.mass[i]  # fertpkg
            S.no_rains = 0
            S.fert_CNT = 1.0

            if fert_app.depth[i] == 0.0:
                S.fert_P_available += fert_app.mass[i] * 0.75
                fert_PST = S.fert_P_available  # TODO fert_PST is frtpst and unused
                S.fert_P_released += fert_app.mass[i] * 0.25

            else:
                S.fert_P_available += fert_app.mass[i] * 0.75 * fert_app.surface_percent[i]
                fert_PST = S.fert_P_available  # TODO above
                S.fert_P_released += fert_app.mass[i] * 0.25 * fert_app.surface_percent[i]

                no = 0
                for n in range(0, 3):
                    if S.listOfSoilLayers[n].bottomDepth >= fert_app.depth[i]:
                        break
                    no += 1

                sum_fac = 0.0

                for w in range(0, 3):
                    S.listOfSoilLayers[w].labile_P *= S.area

                for k in range(0, no):  # TODO weird, can be -1 but that might be intentional
                    S.fact = S.listOfSoilLayers[k].bottomDepth / fert_app.depth[i]
                    S.listOfSoilLayers[k].labile_P += (fert_app.mass[i] * S.fact
                                            * (1.0 - fert_app.surface_percent[i]))
                    sum_fac += S.fact

                S.fact = 1.0 - sum_fac
                S.listOfSoilLayers[no].labile_P += (fert_app.mass[i] * S.fact
                                         * (1.0 - fert_app.surface_percent[i]))

                for w in range(0, 3):
                    S.listOfSoilLayers[w].labile_P /= S.area

