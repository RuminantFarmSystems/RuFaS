################################################################################
"""
SurPhos
File name: p_mineralization.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

# computes P flux between labile and active pools

from math import log, exp


def update_all(S, time):

    day = time.day

    for i in range(0, 3):
        if i == 0:
            S.soil_layers[i].labile_P = S.soil_layers[i].labile_P \
                                                   - S.soil_layers[i].P_uptake \
                                                   * S.soil_layers[0].labile_P \
                                                   / (S.soil_layers[0].labile_P
                                                      + S.soil_layers[1].labile_P * 0.9)
        elif i == 1:
            S.soil_layers[i].labile_P = S.soil_layers[i].labile_P \
                                                   - S.soil_layers[i].P_uptake \
                                                   * S.soil_layers[1].labile_P \
                                                   / (S.soil_layers[0].labile_P
                                                      + S.soil_layers[1].labile_P * 0.9)
        elif i == 2:
            S.soil_layers[i].labile_P = S.soil_layers[i].labile_P \
                                                   - S.soil_layers[i].P_uptake * 0.10

        S.soil_layers[i].labile_P = max(0.0, S.soil_layers[i].labile_P)

        # This code only executes once at the beginning of each year of the simulation
        # count_it and counts are one dimensional arrays of size 3 (standard for
        # representation of soil layers which goes along with the i indexing)
        # each then represents a year counter, count_it beginning at 0 and
        # counts beginning at 1. Both being limited to a 10 year maximum. Counts
        # resets upon reaching that maximum, count_it does not.
        if day == 1:
            if S.count_it[i] < 10:
                S.count_it[i] += 1
            S.counts[i] += 1
            if S.counts[i] == 11:
                S.counts[i] = 1

            # convert soil P from KG/HA to MG/KG

            S.soil_yp[i][S.counts[i]] = S.soil_layers[i].labile_P \
                                        / S.soil_layers[i].bulk_density \
                                        / S.thickness_cm[i] / 0.1
            S.lab_P_sum[i] = 0.0

            for j in range(0, S.count_it[i]):
                S.lab_P_sum[i] += S.soil_yp[i][j]

            S.lab_P_avg[i] = max(0.01, S.lab_P_sum[i] / S.count_it[i])

        S.soil_P[i] = S.soil_layers[i].labile_P / S.soil_layers[i].bulk_density \
                      / S.thickness_cm[i] / 0.1
        S.soil_layers[i].PSP = -0.045 * log(S.soil_layers[i].clay) \
                         + 0.001 * S.soil_layers[i].labile_P \
                         - 0.035 * S.soil_layers[i].org_C + 0.43

        S.soil_layers[i].PSP = max(0.05, min(0.7, S.soil_layers[i].PSP))

        S.soil_layers[i].PSP = (S.PSP_avg[i] * 29.0 + S.soil_layers[i].PSP) / 30.0

        S.PSP_avg[i] = S.soil_layers[i].PSP

        S.pbal[i] = S.soil_layers[i].labile_P - S.soil_layers[i].active_P \
                  * (S.soil_layers[i].PSP / (1.0 - S.soil_layers[i].PSP))

        S.varA[i] = 0.918 * (exp(-4.603 * S.soil_layers[i].PSP))
        S.varB[i] = -0.238 * log(S.varA[i]) - 1.126

        S.base[i] = -1.0 * S.soil_layers[i].PSP + 0.8

        if S.pbal[i] < 0.0:  # TODO: This whole section could be simplified
            S.pflow[i] = 0.0
            S.days[i] = 0.0

            if S.count_day[i] > 0.0:
                S.count_day[i] += 1.0
            if S.count_day[i] == 0.0:
                S.count_day[i] = 1.0

            S.pd_srb_fac[i] = S.base[i] * (S.count_day[i] ** -0.32)
            S.pflow_r[i] = S.pd_srb_fac[i] * S.pbal[i] * -1.0

            if S.pflow_r[i] > S.soil_layers[i].active_P:
                S.pflow_r = S.soil_layers[i].active_P

            S.soil_layers[i].active_P -= S.pflow_r[i]
            S.soil_layers[i].active_P = max(0.0, S.soil_layers[i].active_P)

            S.soil_layers[i].labile_P += S.pflow_r[i]
            S.soil_layers[i].labile_P = max(0.0, S.soil_layers[i].labile_P)

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

            S.pflow[i] = min(S.pflow[i], S.soil_layers[i].labile_P)

            S.soil_layers[i].labile_P -= S.pflow[i]
            S.soil_layers[i].labile_P = max(0.0, S.soil_layers[i].labile_P)

            S.soil_layers[i].active_P += S.pflow[i]
            S.soil_layers[i].active_P = max(0.0, S.soil_layers[i].active_P)

            S.old_pbal[i] = S.pbal[i]

        S.pflow2[i] = 0.0006 * (S.soil_layers[i].stable_P - (4.0 * S.soil_layers[i].active_P))
        S.soil_layers[i].stable_P -= S.pflow2[i]
        S.soil_layers[i].active_P += S.pflow2[i]

        S.temp_lab[i] = S.soil_layers[i].labile_P / S.soil_layers[i].bulk_density \
                      / S.thickness_cm[i] / 0.1
        if S.temp_lab[i] < 5.0:
            min_P = min(((5.0 * S.soil_layers[i].bulk_density * S.thickness_cm[i] * 0.1)
                         - S.soil_layers[i].labile_P), S.soil_layers[i].org_P)
            S.soil_layers[i].labile_P += min_P
            S.soil_layers[i].org_P -= min_P
