################################################################################
"""
SurPhos
File name: soluble_P.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""
################################################################################
from math import exp, log


# calculates the transfer of phosphorus through hydrological processes
# "pseudocode_soil" S.6.E
def update_all(S):
    runoff = S.runoff

    DRP_leachate_prev_layer = 0.0
    for layer in S.soil_layers:
        # convert soil P from KG/HA to MG/KG
        # S.6.E.1
        layer.soil_P = layer.labile_P / layer.bulk_density / layer.thickness_cm / 0.1

        # S.6.E.2
        layer.iso_slope = 173.51 * (layer.clay / 100.0) + 8.48
        layer.iso_inter = 4.726 * layer.iso_slope - 8.97

        # S.6.E.3
        layer.DRP_leachate = min(40.0, exp((layer.soil_P * 1.5 - layer.iso_inter / layer.iso_slope)))

        # S.6.E.4
        if S.soil_layers.index(layer) == 0:
            layer.DRP_runoff = min(layer.labile_P, layer.soil_P * 0.005 * runoff * 0.01)
            layer.labile_P -= layer.DRP_runoff

        # S.6.E.5
        layer.DRP_leachate_act = min(layer.labile_P, layer.DRP_leachate * layer.perc * 0.01)

        layer.labile_P += DRP_leachate_prev_layer
        layer.labile_P -= layer.DRP_leachate_act

        DRP_leachate_prev_layer = layer.DRP_leachate_act

        # S.6.E.6
        S.DRP_runoff_annual += layer.DRP_runoff * S.area

    S.DRP_leachate_annual += DRP_leachate_prev_layer
