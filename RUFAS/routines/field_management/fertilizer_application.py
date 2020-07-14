"""
RuFaS
File name: fertilizer_application.py
Author(s): Jacob Johnson, jacob8399@gmail.com,
           William Donovan, wmdonovan@wisc.edu
"""


def update_all(soil, fert_app):
    """
    Description:
        calculates P added in fertilizer, adds fertilizer P to surface pool,
        and updates cumulative fertilizer P added during model run
        "pseudocode_field_management" FM.3
    Args:
        soil:
        fert_app:
    """

    mass = fert_app['mass']
    surf_perc = fert_app['surface_percent']
    depth = fert_app['depth']

    soil.fert_applied = mass
    soil.no_rains = 0
    soil.fert_CNT = 1.0

    # At the time of application, 75% of applied fertilizer P is
    # available to be released by rain. Until the first rain event,
    # that P is gradually adsorbed by the soil.
    # FM.3.1/2
    soil.fert_P_available += mass * 0.75 * surf_perc
    soil.fert_P_released += mass * 0.25 * surf_perc

    sum_fac = 0.0
    last_layer = 0
    for layer in soil.soil_layers:
        # FM.3.3
        layer.labile_P *= soil.area

        # for each layer above the application depth
        # FM.3.5/6
        if layer.bottom_depth_cm < depth:
            soil.depth_fact = layer.bottom_depth_cm / depth
            layer.labile_P += mass * soil.depth_fact * (1.0 - surf_perc)

            sum_fac += soil.depth_fact
            last_layer += 1

    # for the layer at the application depth
    # FM.3.5/7
    soil.depth_fact = 1.0 - sum_fac
    soil.soil_layers[last_layer].labile_P += mass * soil.depth_fact * (1.0 - surf_perc)

    # S.5.A.8
    for layer in soil.soil_layers:
        layer.labile_P /= soil.area
