
# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself


def update_all(S, time):

    day = time.day
    year = time.year
    till_app = S.tillage_app

    for x in range(len(till_app.day)):
        if till_app.day[x] == day and till_app.year[x] == year:
            for w in range(0, 3):
                S.active_P_layer[w] *= S.area
                S.labile_P_layer[w] *= S.area

            # incorporate surface manure and fertilizer

            S.labile_P_layer[0] += S.fert_p_available * till_app.percent_incorporated[x]
            S.labile_P_layer[0] += S.fert_p_released * till_app.percent_incorporated[x]
            S.fert_p_available -= (S.fert_p_available * till_app.percent_incorporated[x])
            S.fert_p_released -= (S.fert_p_released * till_app.percent_incorporated[x])

            S.labile_P_layer[0] += S.WIP * till_app.percent_incorporated[x]
            S.active_P_layer[0] += S.SIP * till_app.percent_incorporated[x]

            S.WIP -= S.WIP * till_app.percent_incorporated[x]
            S.WOP -= S.WOP * till_app.percent_incorporated[x]
            S.SIP -= S.SIP * till_app.percent_incorporated[x]
            S.SOP -= S.SOP * till_app.percent_incorporated[x]
            S.manure_mass -= S.manure_mass * till_app.percent_incorporated[x]

            for w in range(0, 3):
                S.active_P_layer[w] /= S.area
                S.labile_P_layer[w] /= S.area

            # mix soil

            NLS = 0
            for k in range(0, 3):  # TODO unsure about this
                if till_app.depth[x] > S.depths_layer[k]:
                    break
                NLS = k

            till_soil = 0.0
            till_act_P = 0.0
            till_lab_P = 0.0

            soil_ms = [0, 0, 0]

            for j in range(0, NLS):
                soil_ms[j] = S.bulk_density_layer[j] * S.thick_layer[j] * 100000.0
                till_soil += soil_ms[j]
                till_lab_P += S.labile_P_layer[j]
                till_act_P += S.active_P_layer[j]

            for j in range(0, NLS):
                ratio = soil_ms[j] / till_soil
                S.labile_P_layer[j] = (1.0 - till_app.percent_mixed[x]) \
                                      * S.labile_P_layer[j] + till_lab_P \
                                      * ratio * till_app.percent_mixed[x]
                S.active_P_layer[j] = (1.0 - till_app.percent_mixed[x]) \
                                      * S.active_P_layer[j] + till_act_P \
                                      * ratio * till_app.percent_mixed[x]
