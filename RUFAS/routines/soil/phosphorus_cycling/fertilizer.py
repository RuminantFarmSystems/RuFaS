################################################################################
"""
RuFaS
File name: fertilizer.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################


# calculates P added in fertilizer, adds fertilizer P to surface pool,
# and updates cumulative fertilizer P added during model run
# "pseudocode_soil" S.5.B
def update_all(S, time):

    day = time.day
    year = time.year
    fert_app = S.fertilizer

    for i in range(len(fert_app.day)):
        if fert_app.day[i] == day and fert_app.year[i] - time.start_year + 1 == year:
            S.fert_applied_annual += fert_app.mass[i]  # fertpkg
            S.no_rains = 0
            S.fert_CNT = 1.0

            # At the time of application, 75% of applied fertilizer P is
            # available to be released by rain. Until the first rain event,
            # that P is gradually adsorbed by the soil.
            # S.5.B.1/2
            S.fert_P_available += fert_app.mass[i] * 0.75 * fert_app.surface_percent[i]
            S.fert_P_released += fert_app.mass[i] * 0.25 * fert_app.surface_percent[i]

            sum_fac = 0.0
            last_layer = 0
            for layer in S.soil_layers:
                # S.5.B.3
                layer.labile_P *= S.area

                # for each layer above the application depth
                # S.5.B.5/6
                if layer.bottom_depth_cm < fert_app.depth[i]:
                    S.depth_fact = layer.bottom_depth_cm / fert_app.depth[i]
                    layer.labile_P += fert_app.mass[i] * S.depth_fact * (1.0 - fert_app.surface_percent[i])

                    sum_fac += S.depth_fact
                    last_layer += 1

            # for the layer at the application depth
            # S.5.B.5/7
            S.depth_fact = 1.0 - sum_fac
            S.soil_layers[last_layer].labile_P += fert_app.mass[i] * S.depth_fact * (1.0 - fert_app.surface_percent[i])

            # S.B.4
            for layer in S.soil_layers:
                layer.labile_P /= S.area
