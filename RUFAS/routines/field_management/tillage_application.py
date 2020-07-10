"""
SurPhos
File name: tillage_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


# conducts tillage operations and mixes any manure or fertilizer on
# the surface into the soil and mixes the soil itself
# "pseudocode_soil" S.6.D
def update_all(soil, till_app):

    depth = till_app['depth']
    perc_incorporated = till_app['percent_incorporated']
    perc_mixed = till_app['percent_mixed']

    till_soil_mass = 0.0
    till_act_P = 0.0
    till_lab_P = 0.0

    # attributes of this specific tillage operation
    for layer in soil.soil_layers:
        if layer.bottom_depth_cm <= depth:
            till_soil_mass += layer.mass
            till_act_P += layer.active_P
            till_lab_P += layer.labile_P

    for layer in soil.soil_layers:

        # incorporate surface manure and fertilizer into the first layer
        # S.6.D.1
        if soil.soil_layers.index(layer) == 0:
            # S.6.B.3
            layer.active_P *= soil.area
            layer.labile_P *= soil.area

            layer.labile_P += perc_incorporated * \
                              (soil.fert_P_available + soil.fert_P_released)

            # S.6.D.2
            soil.fert_P_available = soil.fert_P_available - (soil.fert_P_available * perc_incorporated)
            soil.fert_P_released = soil.fert_P_released - (soil.fert_P_released * perc_incorporated)

            # S.6.D.3
            # TODO: RuFaS does not track org P (03.19.20). When it does, WOP/SOP will be incorporated into organic pools
            layer.labile_P += perc_incorporated * soil.WIP
            layer.active_P += perc_incorporated * soil.SIP

            soil.WIP -= soil.WIP * perc_incorporated
            soil.WOP -= soil.WOP * perc_incorporated
            soil.SIP -= soil.SIP * perc_incorporated
            soil.SOP -= soil.SOP * perc_incorporated
            soil.manure_mass -= soil.manure_mass * perc_incorporated

            # S.6.B.4
            layer.active_P /= soil.area
            layer.labile_P /= soil.area

        # Mix soil in accordance with the tillage operation
        # S.6.D.4
        if layer.bottom_depth_cm <= depth:
            ratio = layer.mass / till_soil_mass
            layer.labile_P = (1.0 - perc_mixed) * layer.labile_P \
                             + till_lab_P * ratio * perc_mixed
            layer.active_P = (1.0 - perc_mixed) * layer.active_P \
                             + till_act_P * ratio * perc_mixed
