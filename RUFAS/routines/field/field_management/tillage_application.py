"""
SurPhos
File name: tillage_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


def update_all(soil, till_app):
    """
    Description:
        Conducts tillage operations and mixes any manure or fertilizer on
        the surface into the soil and mixes the soil itself
        "pseudocode_soil" FM.5

    Args:
        soil: an instance of the Soil class defined in sol.py
        till_app: an instance of the BaseApplication class defined in
            field_management.py representing a user defined tillage application
    """
    depth = till_app['depth']
    depth_cm = depth / 10
    percent_incorporated = till_app['percent_incorporated']
    percent_mixed = till_app['percent_mixed']

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
        # FM.5.1
        if soil.soil_layers.index(layer) == 0:
            # S.5.A.7
            layer.active_P *= soil.area
            layer.labile_P *= soil.area

            layer.labile_P += percent_incorporated * \
                              (soil.fert_P_available + soil.fert_P_released)

            # FM.5.2
            soil.fert_P_available = soil.fert_P_available - (soil.fert_P_available * percent_incorporated)
            soil.fert_P_released = soil.fert_P_released - (soil.fert_P_released * percent_incorporated)

            # FM.5.3
            # TODO: RuFaS does not track org P (03.19.20). When it does, WOP/SOP will be incorporated into organic pools
            # TODO: RuFaS does not track org P (03.19.20). When it does, WOP/SOP will be incorporated into organic pools
            layer.labile_P += percent_incorporated * soil.WIP
            layer.active_P += percent_incorporated * soil.SIP

            soil.WIP -= soil.WIP * percent_incorporated
            soil.WOP -= soil.WOP * percent_incorporated
            soil.SIP -= soil.SIP * percent_incorporated
            soil.SOP -= soil.SOP * percent_incorporated
            soil.manure_mass -= soil.manure_mass * percent_incorporated

            # S.5.A.8
            layer.active_P /= soil.area
            layer.labile_P /= soil.area

        # Mix soil in accordance with the tillage operation
        # FM.5.4
        if layer.bottom_depth_cm <= depth_cm:
            ratio = layer.mass / till_soil_mass
            layer.labile_P = (1.0 - percent_mixed) * layer.labile_P \
                             + till_lab_P * ratio * percent_mixed
            layer.active_P = (1.0 - percent_mixed) * layer.active_P \
                             + till_act_P * ratio * percent_mixed
