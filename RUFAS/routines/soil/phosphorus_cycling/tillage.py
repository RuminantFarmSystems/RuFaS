################################################################################
"""
SurPhos
File name: tillage.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################


# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself
# "pseudocode_soil" S.5.D
def update_all(S, time):

    day = time.day
    year = time.year
    till_app = S.tillage

    # determine whether there is a tillage application
    for x in range(len(till_app.day)):
        if till_app.day[x] == day and till_app.year[x] - S.start_year + 1 == year:

            till_soil_mass = 0.0
            till_act_P = 0.0
            till_lab_P = 0.0

            # attributes of this specific tillage operation
            for layer in S.soil_layers:
                if layer.bottom_depth_cm <= till_app.depth[x]:
                    till_soil_mass += layer.mass
                    till_act_P += layer.active_P
                    till_lab_P += layer.labile_P

            for layer in S.soil_layers:

                # incorporate surface manure and fertilizer into the first layer
                # S.5.D.1
                if S.soil_layers.index(layer) == 0:
                    # S.5.B.3
                    layer.active_P *= S.area
                    layer.labile_P *= S.area

                    layer.labile_P += till_app.percent_incorporated[x] * \
                                      (S.fert_P_available + S.fert_P_released)

                    # S.5.D.2
                    S.fert_P_available = S.fert_P_available - (S.fert_P_available * till_app.percent_incorporated[x])
                    S.fert_P_released = S.fert_P_released - (S.fert_P_released * till_app.percent_incorporated[x])

                    # S.5.D.3 TODO: RuFaS does not track org P (03.19.20). When it does, WOP/SOP will be incorporated into organic pools
                    layer.labile_P += till_app.percent_incorporated[x] * S.WIP
                    layer.active_P += till_app.percent_incorporated[x] * S.SIP

                    S.WIP -= S.WIP * till_app.percent_incorporated[x]
                    S.WOP -= S.WOP * till_app.percent_incorporated[x]
                    S.SIP -= S.SIP * till_app.percent_incorporated[x]
                    S.SOP -= S.SOP * till_app.percent_incorporated[x]
                    S.manure_mass -= S.manure_mass * till_app.percent_incorporated[x]

                    # S.5.B.4
                    layer.active_P /= S.area
                    layer.labile_P /= S.area

                # Mix soil in accordance with the tillage operation
                # S.5.D.4
                if layer.bottom_depth_cm <= till_app.depth[x]:
                    ratio = layer.mass / till_soil_mass
                    layer.labile_P = (1.0 - till_app.percent_mixed[x]) * layer.labile_P \
                                     + till_lab_P * ratio * till_app.percent_mixed[x]
                    layer.active_P = (1.0 - till_app.percent_mixed[x]) * layer.active_P \
                                     + till_act_P * ratio * till_app.percent_mixed[x]
