"""
RUFAS
SurPhos

File name: soluble_P.py

Author(s):  DR. Peter A. Vadas
            USDA-ARS Dairy Forage Research Center
            E-mail: peter.vadas@ars.usda.gov

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""

from math import exp, log


def update_all(soil):
    """
    Description:
        calculates the transfer of phosphorus through hydrological processes
        "pseudocode_soil" S.5.B
    Args:
        soil: an instance of the Soil class specified in soil.py
    """

    runoff = soil.runoff

    DRP_leachate_prev_layer = 0.0
    for layer in soil.soil_layers:
        # convert soil P from KG/HA to MG/KG
        # S.5.B.1
        layer.soil_P = layer.labile_P / layer.bulk_density / layer.thickness_cm / 0.1

        # S.5.B.2
        layer.iso_slope = 173.51 * (layer.clay / 100.0) + 8.48
        layer.iso_inter = 4.726 * layer.iso_slope - 8.97

        # S.5.B.3
        # this if statement avoids a range error that can happen within the exp()
        if ((layer.soil_P * 1.5 - layer.iso_inter) / layer.iso_slope) <= log(40):
            layer.DRP_leachate = min(40.0, exp((layer.soil_P * 1.5 - layer.iso_inter) / layer.iso_slope))
        else:
            layer.DRP_leachate = 40

        # S.5.B.4
        if soil.soil_layers.index(layer) == 0:
            layer.DRP_runoff = min(layer.labile_P, layer.soil_P * 0.005 * runoff * 0.01)
            layer.labile_P -= layer.DRP_runoff

        # S.5.B.5
        layer.DRP_leachate_act = min(layer.labile_P, layer.DRP_leachate * layer.percolation * 0.01)

        layer.labile_P += DRP_leachate_prev_layer
        layer.labile_P -= layer.DRP_leachate_act

        DRP_leachate_prev_layer = layer.DRP_leachate_act

        # S.5.B.6
        soil.DRP_runoff += layer.DRP_runoff * soil.area

    soil.DRP_drainage += DRP_leachate_prev_layer
