
# computes P flux between labile and active pools

from math import log, exp


def update_all(S, time):

    year = time.year
    day = time.day
    crop_P_up = S.crop_P_uptake

    lab_P_sum = [0, 0, 0]
    lab_P_avg = [0, 0, 0]

    pbal = [0, 0, 0]  # TODO no idea what this means
    varA = [0, 0, 0]
    varB = [0, 0, 0]
    base = [0, 0, 0]
    pflow = [0, 0, 0]
    days = [0, 0, 0]
    cnt_day = [0, 0, 0]
    pd_srd_fac = [0, 0, 0]
    pflow_r = [0, 0, 0]
    old_pbal = [0, 0, 0]
    PSP_fac = [0, 0, 0]
    pflow2 = [0, 0, 0]
    temp_lab = [0, 0, 0]

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
            lab_P_sum[i] = 0

            for j in range(0, S.count_it[i]):
                lab_P_sum[i] += S.soil_yp[i][j]

            lab_P_avg[i] = lab_P_sum[i] / S.count_it[i]
            if lab_P_avg[i] < 0.01:
                lab_P_avg[i] = 0.01

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
        S.PSP_avg[i] = S.PSP_layer[i]  # TODO psp_avg is unnecessary

        pbal[i] = S.labile_P_layer[i] - S.active_P_layer[i] \
                  * (S.PSP_layer[i] / (1.0 - S.PSP_layer[i]))

        varA[i] = 0.918 * (exp(-4.603 * S.PSP_layer[i]))
        varB[i] = -0.238 * log(varA[i]) - 1.126

        base[i] = -1.0 * S.PSP_layer[i] + 0.8

        if pbal[i] < 0.0:
            pflow[i] = 0.0
            days[i] = 0.0

            if cnt_day[i] > 0.0:
                cnt_day[i] += 1.0
            if cnt_day[i] == 0.0:
                cnt_day[i] = 1.0

            pd_srd_fac[i] = base[i] * (cnt_day[i] ** -0.32)
            pflow_r[i] = pd_srd_fac[i] * pbal[i] * -1.0

            if pflow_r[i] > S.active_P_layer[i]:
                pflow_r = S.active_P_layer[i]

            S.active_P_layer[i] -= pflow_r[i]
            if S.active_P_layer[i] <= 0.0:
                S.active_P_layer[i] = 0.0

            S.labile_P_layer[i] += pflow_r[i]
            if S.labile_P_layer[i] <= 0.0:
                S.labile_P_layer[i] = 0.0

        elif pbal[i] >= 0.0:
            pflow_r[i] = 0.0
            cnt_day[i] = 0.0

            if pbal[i] > old_pbal[i]:
                days[i] = 0.0
            if days[i] >= 1.0:
                days[i] += 1.0
            if days[i] == 0.0:
                days[i] = 1.0

            PSP_fac[i] = varA[i] * (days[i] ** varB[i])
            pflow[i] = PSP_fac[i] * pbal[i]

            # TODO next two if statements are redundant
            if pflow[i] > S.labile_P_layer[i]:
                pflow[i] = S.labile_P_layer[i]

            S.labile_P_layer[i] -= pflow[i]
            if S.labile_P_layer[i] <= 0.0:
                S.labile_P_layer[i] = 0.0

            S.active_P_layer[i] += pflow[i]
            if S.active_P_layer[i] <= 0:
                S.active_P_layer[i] = 0.0

            old_pbal[i] = pbal[i]  # TODO why is this not done in both?

        pflow2[i] = 0.0006 * (S.stable_P_layer[i] - (4.0 * S.active_P_layer[i]))
        S.stable_P_layer[i] -= pflow2[i]
        S.active_P_layer[i] += pflow2[i]

        temp_lab[i] = S.labile_P_layer[i] / S.bulk_density_layer[i] \
                      / S.thick_layer[i] / 0.1
        if temp_lab[i] < 5.0:
            min_P = min(((5.0 * S.bulk_density_layer[i] * S.thick_layer[i] * 0.1)
                         - S.labile_P_layer[i]), S.org_P_layer[i])
            S.labile_P_layer[i] += min_P
            S.org_P_layer[i] -= min_P
