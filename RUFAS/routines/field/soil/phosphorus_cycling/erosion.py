"""
RUFAS

File name: erosion.py

Author(s):  DR. Melissa Motew
            USDA-ARS Dairy Forage Research Center

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""


def update_all(soil):
    """
    Description:
        TODO: Peter was skeptical about the compatibility of this module with SurPhos
        Calculates sediment P transported in runoff using SWAT
        "pseudocode_soil" S.6.I
    Args:
        soil: instance of the Soil class specified in soil.py
    """

    soil.runoff_conc = 0
    soil.enrichment_P = 0
    if soil.runoff != 0:
        # S.6.I.4
        soil.runoff_conc = soil.sed / (10 * soil.area * soil.runoff)

        # S.6.I.3
        soil.enrichment_P = 0.78 * (soil.runoff_conc ** -0.2468)

    # S.6.I.2
    soil.soil_layers[0].active_P *= soil.area
    soil.soil_layers[0].stable_P *= soil.area

    soil.sed_P_conc = 100 * (soil.soil_layers[0].active_P + soil.soil_layers[0].stable_P) \
                      / (soil.soil_layers[0].bulk_density * soil.soil_layers[0].bottom_depth)

    # S.6.I.1
    soil.sed_P = 0.001 * soil.sed_P_conc * (soil.sed / soil.area) * soil.enrichment_P

    soil.soil_layers[0].active_P -= soil.soil_layers[0].active_P * \
                                    (soil.sed_P / (soil.soil_layers[0].active_P + soil.soil_layers[0].stable_P))

    soil.soil_layers[0].stable_P -= soil.soil_layers[0].stable_P * \
                                    (soil.sed_P / (soil.soil_layers[0].active_P + soil.soil_layers[0].stable_P))

    soil.soil_layers[0].active_P /= soil.area
    soil.soil_layers[0].stable_P /= soil.area
