################################################################################
"""
SurPhos
File name: p_mineralization.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################

from math import log, exp


# computes P flux between labile and active pools
# "pseudocode_soil" S.5.H
def update_all(S, time):

    # S.5.H.1
    uptake_fact = 0.1
    S.soil_layers[-1].labile_P_uptake = min(S.soil_layers[-1].labile_P, S.soil_layers[-1].P_uptake * uptake_fact)
    S.soil_layers[-1].labile_P -= S.soil_layers[-1].labile_P_uptake
    for x in range(len(S.soil_layers) - 2, 0, -1):
        layer = S.soil_layers[x]
        prev_layer = S.soil_layers[x + 1]

        uptake_fact = layer.labile_P / layer.labile_P + prev_layer.labile_P * 0.9

        layer.labile_P_uptake = min(layer.labile_P, layer.P_uptake * uptake_fact)
        layer.labile_P -= layer.labile_P_uptake

        # S.5.H.3
        layer.labile_P_sum += layer.labile_P
        layer.labile_P_avg = layer.labile_P_sum / (time.year * time.day)

        # S.5.H.4
        layer.soil_P = layer.labile_P / layer.bulk_density / layer.thickness_cm / 0.1

        # S.5.H.2
        layer.PSP_max = -0.045 * log(layer.clay) + 0.001 * layer.labile_P_avg - 0.035 * layer.org_C + 0.43

        # S.5.H.5
        layer.PSP_act = max(0.05, min(0.7, layer.PSP_max))
        layer.PSP_act = ((layer.PSP_avg * 29.0) + layer.PSP_act) / 30.0
        layer.PSP_avg = layer.PSP_act

        # S.5.H.6
        layer.pbal = layer.labile_P - layer.active_P * (layer.PSP_act / (1.0 - layer.PSP_act))

        # S.5.H.7
        varA = 0.918 * exp(-4.603 * layer.PSP_act)
        varB = -0.238 * log(varA) - 1.126
        base = -layer.PSP_act + 0.8

        # S.5.H.8
        if layer.pbal < 0.0:
            layer.days_unbalanced_labile += 1.0
            PD_fac = base * (layer.days_unbalanced_labile ** -0.32)

            # S.5.H.9
            labile_pflow = min(layer.active_P, (-1) * PD_fac * layer.pbal)

            layer.active_P -= labile_pflow
            layer.labile_P += labile_pflow

        # S.5.H.10
        elif layer.pbal >= 0.0:
            layer.days_unbalanced_active += 1.0
            PS_fac = varA * (layer.days_unbalanced_active ** varB)

            # S.5.H.11
            active_pflow = min(layer.labile_P, PS_fac * layer.pbal)

            layer.labile_P -= active_pflow
            layer.active_P += active_pflow

        else:
            layer.days_unbalanced_labile = 0.0
            layer.days_unbalanced_active = 0.0

        # S.5.H.12
        stable_pflow = min(layer.stable_P, 0.0006 * (layer.stable_P - (4.0 * layer.active_P)))

        layer.stable_P -= stable_pflow
        layer.active_P += stable_pflow

        # S.5.H.13
        if (layer.labile_P / layer.bulk_density / layer.thickness_cm / 0.1) < 5.0:
            min_P = min(layer.org_P, (5.0 * layer.bulk_density * layer.thickness_cm * 0.1) - layer.labile_P)

            layer.org_P -= min_P
            layer.labile_P += min_P

        S.soil_layers[x] = layer
