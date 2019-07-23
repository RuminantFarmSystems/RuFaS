
# computes P flux between labile and active pools

from math import log, exp


def update_all(S, time):

    year = time.year
    day = time.day
    crop_P_up = S.crop_P_uptake

    for i in range(0, 3):
        if i == 0:
            S.labile_P_layer[i] = S.labile_P_layer[i] - crop_P_up.P_uptake_daily[year][day - 1] \
                                   * S.labile_P_layer[0] / (S.labile_P_layer[0]
                                                            + S.labile_P_layer[1] * 0.9)
        elif i == 1:
            S.labile_P_layer[i] = S.labile_P_layer[i] - crop_P_up.P_uptake_daily[year][day - 1] \
                                   * S.labile_P_layer[1] / (S.labile_P_layer[0]
                                                            + S.labile_P_layer[1] * 0.9)
        elif i == 2:
            S.labile_P_layer[i] = S.labile_P_layer[i] - crop_P_up.P_uptake_daily[year][day - 1] * 0.10

        S.labile_P_layer[i] = max(0.0, S.labile_P_layer[i])

        if day == 1:
            S.count_it[i] += 1
            if S.count_it[i] > 10:
                S.count_it = 10
            S.counts[i] += 1
            if S.counts[i] == 11:
                S.counts[i] = 1

            # convert soil P from KG/HA to MG/KG

            S.soil_yp[i][S.counts[i]] = S.labile_P_layer[i] / S.bulk_density_layer[i] \
                                        / S.thick_layer[i] / 0.1
            S.lab_P_sum[i] = 0

            for j in range(0, S.count_it[i]):
                S.lab_P_sum[i] += S.soil_yp[i][j]

            S.lab_P_avg[i] = S.lab_P_sum[i] / S.count_it[i]
            if S.lab_P_avg[i] < 0.01:
                S.lab_P_avg[i] = 0.01

        S.soil_P[i] = S.labile_P_layer[i] / S.bulk_density_layer[i] \
                      / S.thick_layer[i] / 0.1
        S.PSP_layer[i] = -0.045 * log(S.clay_layer[i]) \
                         + 0.001 * S.labile_P_layer[i] \
                         - 0.035 * S.OC_layer[i] + 0.43

        if S.PSP_layer[i] < 0.05:
            S.PSP_layer[i] = 0.05
        elif S.PSP_layer[i] > 0.7:
            S.PSP_layer[i] = 0.7

        S.PSP_layer[i] = (S.PSP_avg[i] * 29.0 + S.PSP_layer[i]) / 30.0

        S.PSP_avg[i] = S.PSP_layer[i]

        S.pbal[i] = S.labile_P_layer[i] - S.active_P_layer[i] \
                  * (S.PSP_layer[i] / (1.0 - S.PSP_layer[i]))

        S.varA[i] = 0.918 * (exp(-4.603 * S.PSP_layer[i]))
        S.varB[i] = -0.238 * log(S.varA[i]) - 1.126

        S.base[i] = -1.0 * S.PSP_layer[i] + 0.8

        if S.pbal[i] < 0.0:
            S.pflow[i] = 0.0
            S.days[i] = 0.0

            if S.count_day[i] > 0.0:
                S.count_day[i] += 1.0
            if S.count_day[i] == 0.0:
                S.count_day[i] = 1.0

            S.pd_srb_fac[i] = S.base[i] * (S.count_day[i] ** -0.32)
            S.pflow_r[i] = S.pd_srb_fac[i] * S.pbal[i] * -1.0

            if S.pflow_r[i] > S.active_P_layer[i]:
                S.pflow_r = S.active_P_layer[i]

            S.active_P_layer[i] -= S.pflow_r[i]
            if S.active_P_layer[i] <= 0.0:
                S.active_P_layer[i] = 0.0

            S.labile_P_layer[i] += S.pflow_r[i]
            if S.labile_P_layer[i] <= 0.0:
                S.labile_P_layer[i] = 0.0

        elif S.pbal[i] >= 0.0:
            S.pflow_r[i] = 0.0
            S.count_day[i] = 0.0

            if S.pbal[i] > S.old_pbal[i]:
                S.days[i] = 0.0
            if S.days[i] >= 1.0:
                S.days[i] += 1.0
            if S.days[i] == 0.0:
                S.days[i] = 1.0

            S.PSP_fac[i] = S.varA[i] * (S.days[i] ** S.varB[i])
            S.pflow[i] = S.PSP_fac[i] * S.pbal[i]

            # TODO next two if statements are redundant
            if S.pflow[i] > S.labile_P_layer[i]:
                S.pflow[i] = S.labile_P_layer[i]

            S.labile_P_layer[i] -= S.pflow[i]
            if S.labile_P_layer[i] <= 0.0:
                S.labile_P_layer[i] = 0.0

            S.active_P_layer[i] += S.pflow[i]
            if S.active_P_layer[i] <= 0:
                S.active_P_layer[i] = 0.0

            S.old_pbal[i] = S.pbal[i]  # TODO why is this not done in both?

        S.pflow2[i] = 0.0006 * (S.stable_P_layer[i] - (4.0 * S.active_P_layer[i]))
        S.stable_P_layer[i] -= S.pflow2[i]
        S.active_P_layer[i] += S.pflow2[i]

        S.temp_lab[i] = S.labile_P_layer[i] / S.bulk_density_layer[i] \
                      / S.thick_layer[i] / 0.1
        if S.temp_lab[i] < 5.0:
            min_P = min(((5.0 * S.bulk_density_layer[i] * S.thick_layer[i] * 0.1)
                         - S.labile_P_layer[i]), S.org_P_layer[i])
            S.labile_P_layer[i] += min_P
            S.org_P_layer[i] -= min_P
