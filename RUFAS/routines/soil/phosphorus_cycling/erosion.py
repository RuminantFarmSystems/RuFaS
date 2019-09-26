################################################################################
"""
SurPhos
File name: erosion.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


################################################################################


def update_all(S):
    S.runoff_conc = 0
    S.enrichment_P = 0
    if S.runoff != 0:
        S.runoff_conc = S.sed / (10 * S.area * S.runoff)
        S.enrichment_P = 0.78 * (S.runoff_conc ** -0.2468)

    S.sed_P_conc = 100 * (S.soil_layers[0].active_P + S.soil_layers[0].stable_P) \
                   / (S.soil_layers[0].bulk_density * S.soil_layers[0].bottom_depth)

    S.sed_P = 0.001 * S.sed_P_conc * (S.sed / S.area) * S.enrichment_P

    S.soil_layers[0].active_P -= S.soil_layers[0].active_P * \
                                 (S.sed_P / S.soil_layers[0].active_P + S.soil_layers[0].stable_P)

    S.soil_layers[0].stable_P -= S.soil_layers[0].stable_P * \
                                 (S.sed_P / S.soil_layers[0].active_P + S.soil_layers[0].stable_P)
