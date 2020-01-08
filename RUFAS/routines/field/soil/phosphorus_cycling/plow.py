################################################################################
"""
SurPhos
File name: plow.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself


def update_all(S, time):

    day = time.day
    year = time.year
    till_app = S.tillage

    for i in range(len(till_app.day)):
        if (till_app.day[i] == day and till_app.year[i] - S.start_year + 1 == year) \
                or (till_app.year[i] - S.start_year + 1 == year and till_app.day[i] == -1
                    and S.tillage_day is True):
            print(time.year, time.day)
            for w in range(0, 3):
                S.soil_layers[w].active_P *= S.area
                S.soil_layers[w].labile_P *= S.area

            # incorporate surface manure and fertilizer

            S.soil_layers[0].labile_P += till_app.percent_incorporated[i] * (S.fert_P_available
                                                                                  + S.fert_P_released)

            S.fert_P_available = S.fert_P_available - (S.fert_P_available * till_app.percent_incorporated[i])
            S.fert_P_released = S.fert_P_released - (S.fert_P_released * till_app.percent_incorporated[i])

            S.soil_layers[0].labile_P += till_app.percent_incorporated[i] * S.WIP
            S.soil_layers[0].active_P += till_app.percent_incorporated[i] * S.SIP

            S.WIP -= S.WIP * till_app.percent_incorporated[i]
            S.WOP -= S.WOP * till_app.percent_incorporated[i]
            S.SIP -= S.SIP * till_app.percent_incorporated[i]
            S.SOP -= S.SOP * till_app.percent_incorporated[i]
            S.manure_mass -= S.manure_mass * till_app.percent_incorporated[i]

            for w in range(0, 3):
                S.soil_layers[w].active_P /= S.area
                S.soil_layers[w].labile_P /= S.area

            # mix soil

            NLS = 0
            for k in range(0, 3):
                if not till_app.depth[i] > S.soil_layers[k].bottom_depth_cm:
                    NLS = k
                    break

            till_soil = 0.0
            till_act_P = 0.0
            till_lab_P = 0.0

            for j in range(0, NLS + 1):
                S.soil_mass[j] = S.soil_layers[j].bulk_density * S.thickness_cm[j] * 100000.0
                till_soil += S.soil_mass[j]
                till_lab_P += S.soil_layers[j].labile_P
                till_act_P += S.soil_layers[j].active_P

            for j in range(0, NLS + 1):
                ratio = S.soil_mass[j] / till_soil
                S.soil_layers[j].labile_P = (1.0 - till_app.percent_mixed[i]) \
                                      * S.soil_layers[j].labile_P + till_lab_P \
                                      * ratio * till_app.percent_mixed[i]
                S.soil_layers[j].active_P = (1.0 - till_app.percent_mixed[i]) \
                                      * S.soil_layers[j].active_P + till_act_P \
                                      * ratio * till_app.percent_mixed[i]
