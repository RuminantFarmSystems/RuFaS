"""
SurPhos
File name: tillage.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""

# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself

from RUFAS.routines.field.application_management import application_management


def update_all(S, application, weather, time):

    day = time.day
    year = time.year
    till_app = application.tillage

    for i in range(len(till_app.day)):
        if (till_app.day[i] == day and till_app.year[i] - S.start_year + 1 == year) \
                or (till_app.year[i] - S.start_year + 1 == year and till_app.day[i] == -1
                    and application.tillage_day is True):

            till_soil_mass = 0.0
            till_act_P = 0.0
            till_lab_P = 0.0

            if not application_management.check_conditions(S, application, weather, time, i, 't'):

                # attributes of this specific tillage operation
                for layer in S.soil_layers:
                    if layer.bottom_depth_cm <= till_app.depth[i]:
                        till_soil_mass += layer.mass
                        till_act_P += layer.active_P
                        till_lab_P += layer.labile_P

                for layer in S.soil_layers:

                    # incorporate surface manure and fertilizer into the first layer
                    # S.6.D.1
                    if S.soil_layers.index(layer) == 0:
                        # S.6.B.3
                        layer.active_P *= S.area
                        layer.labile_P *= S.area

                        layer.labile_P += till_app.percent_incorporated[i] * \
                                          (S.fert_P_available + S.fert_P_released)

                        # S.6.D.2
                        S.fert_P_available = S.fert_P_available - \
                                             (S.fert_P_available * till_app.percent_incorporated[i])
                        S.fert_P_released = S.fert_P_released - \
                                            (S.fert_P_released * till_app.percent_incorporated[i])

                        # S.6.D.3 TODO: RuFaS does not track org P (03.19.20).
                        layer.labile_P += till_app.percent_incorporated[i] * S.WIP
                        layer.active_P += till_app.percent_incorporated[i] * S.SIP

                        S.WIP -= S.WIP * till_app.percent_incorporated[i]
                        S.WOP -= S.WOP * till_app.percent_incorporated[i]
                        S.SIP -= S.SIP * till_app.percent_incorporated[i]
                        S.SOP -= S.SOP * till_app.percent_incorporated[i]
                        S.manure_mass -= S.manure_mass * till_app.percent_incorporated[i]

                        # S.6.B.4
                        layer.active_P /= S.area
                        layer.labile_P /= S.area

                    # Mix soil in accordance with the tillage operation
                    # S.6.D.4
                    if layer.bottom_depth_cm <= till_app.depth[i]:
                        ratio = layer.mass / till_soil_mass
                        layer.labile_P = (1.0 - till_app.percent_mixed[i]) * layer.labile_P \
                                         + till_lab_P * ratio * till_app.percent_mixed[i]
                        layer.active_P = (1.0 - till_app.percent_mixed[i]) * layer.active_P \
                                         + till_act_P * ratio * till_app.percent_mixed[i]
