"""
RUFAS
SurPhos

File name: tillage.py

Author(s):  DR. Peter A. Vadas
            USDA-ARS Dairy Forage Research Center
            E-mail: peter.vadas@ars.usda.gov

Coder(s):   Jacob Johnson jacob8399@gmail.com
            William Donovan wmdonovan@wisc.edu
"""


def update_all(soil, till_app):
    """
    Description:
        conducts tillage operations and mixes any manure or fertilizer on
        the surface into the soil and mixes the soil itself
    Args:
        soil: an instance of the Soil class specified in soil.py
        till_app: an instance of the Tillage class specified in
            field_management.py
    """
    depth = till_app['depth']
    # adjustment to cm because SurPhos was originally created in cm but
    # RuFaS uses mm
    depth_cm = depth / 10
    perc_incorporated = till_app['percent_incorporated']
    perc_mixed = till_app['percent_mixed']

    till_soil_mass = 0.0
    till_act_P = 0.0
    till_lab_P = 0.0

    # attributes of this specific tillage operation
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm <= depth_cm:
            till_soil_mass += layer.mass
            till_act_P += layer.active_P
            till_lab_P += layer.labile_P

    for layer in soil.soil_layers:

        # incorporate surface manure and fertilizer into the first layer
        # S.5.D.1
        if soil.soil_layers.index(layer) == 0:
            # S.5.B.3
            layer.active_P *= soil.area
            layer.labile_P *= soil.area

            layer.labile_P += perc_incorporated * \
                              (soil.fert_P_available + soil.fert_P_released)

            # S.5.D.2
            soil.fert_P_available = soil.fert_P_available - \
                                    (soil.fert_P_available * perc_incorporated)
            soil.fert_P_released = soil.fert_P_released - \
                                   (soil.fert_P_released * perc_incorporated)

            # S.5.D.3 TODO: RuFaS does not track org P (03.19.20).
            layer.labile_P += perc_incorporated * soil.WIP
            layer.active_P += perc_incorporated * soil.SIP

            soil.WIP -= soil.WIP * perc_incorporated
            soil.WOP -= soil.WOP * perc_incorporated
            soil.SIP -= soil.SIP * perc_incorporated
            soil.SOP -= soil.SOP * perc_incorporated
            soil.manure_mass -= soil.manure_mass * perc_incorporated

            # S.5.B.4
            layer.active_P /= soil.area
            layer.labile_P /= soil.area

        # Mix soil in accordance with the tillage operation
        # S.5.D.4
        if layer.bottom_depth_cm <= depth_cm:
            ratio = layer.mass / till_soil_mass
            layer.labile_P = (1.0 - perc_mixed) * layer.labile_P \
                             + till_lab_P * ratio * perc_mixed
            layer.active_P = (1.0 - perc_mixed) * layer.active_P \
                             + till_act_P * ratio * perc_mixed
