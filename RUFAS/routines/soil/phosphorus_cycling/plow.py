################################################################################
"""
SurPhos
File name: plow.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           WIlliam Donovan, wmdonovan@wisc.edu
"""
################################################################################

# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself


def update_all(S, time):

    day = time.day
    year = time.year
    till_app = S.tillage

    for x in range(len(till_app.day)):
        if till_app.day[x] == day and till_app.year[x] - S.start_year + 1 == year:
            for w in range(0, 3):
                S.listOfSoilLayers[w].active_P *= S.area
                S.listOfSoilLayers[w].labile_P *= S.area

            # incorporate surface manure and fertilizer

            # TODO math
            S.listOfSoilLayers[0].labile_P += till_app.percent_incorporated[x] * (S.fert_P_available + S.fert_P_released)

            S.fert_P_available = S.fert_P_available - (S.fert_P_available * till_app.percent_incorporated[x])
            S.fert_P_released = S.fert_P_released - (S.fert_P_released * till_app.percent_incorporated[x])

            # TODO math
            S.listOfSoilLayers[0].labile_P += till_app.percent_incorporated[x] * (S.SIP + S.WIP)

            S.WIP -= S.WIP * till_app.percent_incorporated[x]
            S.WOP -= S.WOP * till_app.percent_incorporated[x]
            S.SIP -= S.SIP * till_app.percent_incorporated[x]
            S.SOP -= S.SOP * till_app.percent_incorporated[x]
            S.manure_mass -= S.manure_mass * till_app.percent_incorporated[x]

            for w in range(0, 3):
                S.listOfSoilLayers[w].active_P /= S.area
                S.listOfSoilLayers[w].labile_P /= S.area

            # mix soil

            NLS = 0
            for k in range(0, 3):
                if till_app.depth[x] > S.depths_layer[k]:
                    break
                NLS = k

            till_soil = 0.0
            till_act_P = 0.0
            till_lab_P = 0.0

            for j in range(0, NLS):
                S.soil_ms[j] = S.listOfSoilLayers[j].bulkDensity * S.thick_layer[j] * 100000.0
                till_soil += S.soil_ms[j]
                till_lab_P += S.listOfSoilLayers[j].labile_P
                till_act_P += S.listOfSoilLayers[j].active_P
                # TODO used to be two for loops split here, same header
                ratio = S.soil_ms[j] / till_soil
                S.listOfSoilLayers[j].labile_P = (1.0 - till_app.percent_mixed[x]) \
                                      * S.listOfSoilLayers[j].labile_P + till_lab_P \
                                      * ratio * till_app.percent_mixed[x]
                S.listOfSoilLayers[j].active_P = (1.0 - till_app.percent_mixed[x]) \
                                      * S.listOfSoilLayers[j].active_P + till_act_P \
                                      * ratio * till_app.percent_mixed[x]
